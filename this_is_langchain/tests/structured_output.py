from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
# 通用 JSON Schema
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


# 创建模型
llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
model = llm.with_structured_output(schema=nutrients_schema)

# 定义提示词
prompt = """
请将以下内容转换为指定的结构化JSON格式，每个营养素（如维生素、矿物质、脂肪酸等）对应一个数组，数组中是与之相关的食物。

1. **钙**：牛奶、奶酪、酸奶、羽衣甘蓝、芝麻。
2. **铁**：红肉、菠菜、扁豆、肝脏。
3. **膳食纤维**：燕麦、糙米、黑豆、苹果、梨。
"""

# 期望的输出：
# {'钙': ['牛奶', '奶酪', '酸奶', '羽衣甘蓝', '芝麻'], '铁': ['红肉', '菠菜', '扁豆', '肝脏'], '膳食纤维': ['燕麦', '糙米', '黑豆', '苹果', '梨']}

# 获取结构化数据
structured_output = model.invoke(prompt)
print(structured_output)
