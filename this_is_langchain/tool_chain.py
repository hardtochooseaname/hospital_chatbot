from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from deep_translator import GoogleTranslator
from langchain.schema.runnable import RunnableLambda
from pprint import pprint
import time

from spoonacular import get_food_nutrients_info

load_dotenv()

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )



def extract_nutrient_food_mapping(input, llm):
    print("\n>>> Extracting nutrient-food mapping from input...")

    # 定义提示词
    human_message = """
请将以下内容中**有关营养素及其相关食物**的部分，转换为指定的结构化 JSON 格式。
忽略输入中与营养素和相关食物无关的内容，包括描述性文字、提示性语言、建议或其他无关句子。
输出时只需提供结构化 JSON 数据，不需要额外的文字说明。

每个营养素（如某维生素、微量元素、脂肪酸等）对应一个数组，数组中是与之相关的食物。例如：

输入：
多摄入维生素A、E和不饱和脂肪酸有助于改善粗糙干燥的皮肤。富含这些营养的食物有：
1. 维生素A：胡萝卜、红薯、菠菜
2. 维生素E：坚果、种子、鳄梨
3. 不饱和脂肪酸：三文鱼、亚麻籽、橄榄油
平时也要注意多喝水保持身体水分充足。

输出：
{{
"维生素A": ["胡萝卜", "红薯", "菠菜"],
"维生素E": ["坚果", "种子", "鳄梨"],
"不饱和脂肪酸": ["三文鱼", "亚麻籽", "橄榄油"]
}}

输出内容限制：仅输出结构化 JSON 数据，不包含任何其他标记、解释或修饰符号。
请将以下内容按上述规则处理：
{input}
"""

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个关键词提取助手，可以帮我从文本中提取出我想要的关键词，并以我指定的json结构返回。"),
            ("human", human_message),
        ]
    )
    
    # 定义通用 JSON Schema
    nutrients_schema = {
        "title": "Nutritional Information",
        "description": "A mapping of nutrients to their related foods.",
        "type": "object",
        "patternProperties": {
            ".*": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of foods associated with the nutrient.",
            }
        },
        "additionalProperties": False
    }
    
    llm_with_structured_output = llm.with_structured_output(schema=nutrients_schema)

    chain = prompt_template | llm_with_structured_output 

    structured_output = chain.invoke({'input': input})
    pprint(structured_output)
    return structured_output


def translate_to_english(data):
    print("\n>>> Translating output into English...")
    translator = GoogleTranslator(source="chinese (simplified)", target="en")
    translated_data = {}
    for nutrient, foods in data.items():
        translated_nutrient = translator.translate(nutrient)
        translated_foods = [translator.translate(food) for food in foods]
        translated_data[translated_nutrient] = translated_foods
        time.sleep(0.2)
    pprint(translated_data)
    return translated_data


def retrieve_all_food_nutrition_info(food_nutrients_dict):
    print("\n>>> Retrieving nutrients info from api...")
    result_strings = []
    for nutrient, foods in food_nutrients_dict.items():
        nutrient_section = ["\n***************************************"]
        nutrient_section.append(f"\n{nutrient}:\n")
        
        for food in foods:
            try:
                # 获取食物的详细营养信息
                food_info = get_food_nutrients_info(food)
                # 翻译成中文
                nutrient_section.append(food_info)
            except Exception as e:
                nutrient_section.append(f"Error retrieving data for {food}: {str(e)}")
        
        nutrient_section.append("\n")
        result_strings.append("\n".join(nutrient_section))
    
    # 合并所有营养素的字符串部分
    result = "\n".join(result_strings)
    print(result)
    return result


def translate_to_chinese_with_format(data):
    print("\n>>> Tanslating string into Chinese...")
    # 分割为行，逐行翻译
    lines = data.splitlines()
    translated_lines = []
    translator = GoogleTranslator(source='en', target='chinese (simplified)')
    
    time.sleep(1)
    print("--- sleeping for api calling ---")
    i = 0
    for line in lines:
        i += 1
        if i % 10 == 0:
            print("--- sleeping for api calling ---")
            time.sleep(1)
        # 检测前导空白
        leading_spaces = len(line) - len(line.lstrip())
        # 翻译非空行
        if line.strip():
            translated_text = translator.translate(line.strip())
            # 恢复前导空白
            translated_lines.append(" " * leading_spaces + translated_text)
        else:
            # 空行直接添加
            translated_lines.append("")
    
    # 合并行并返回
    return "\n".join(translated_lines)


input = """"
有助于睡眠的营养素及食物来源：

1. 色氨酸：牛奶。

2. 镁：坚果。

3. B族维生素：鸡蛋。
"""

nutrient_food_mapping_extractor = RunnableLambda(lambda x: extract_nutrient_food_mapping(x, llm))
structured_data_translator = RunnableLambda(lambda x: translate_to_english(x))
nutrients_info_retriever = RunnableLambda(lambda x: retrieve_all_food_nutrition_info(x))
string_translator = RunnableLambda(lambda x: translate_to_chinese_with_format(x))

chain = nutrient_food_mapping_extractor | structured_data_translator | nutrients_info_retriever | string_translator
result = chain.invoke(input)

print(result)
