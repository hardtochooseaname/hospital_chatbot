from Questionnaire import diabetes_questionnaire
from dotenv import load_dotenv
#from langchain import hub
# from langchain.agents import (
#     AgentExecutor,
#     create_react_agent,
# )
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import sys
from rag.retrieve import query_in_vectorstore

patient = {
    "name": "张三",
    "age": 18,
    "gender": "男",
    "disease": "糖尿病",
    "questionnaire": diabetes_questionnaire
}

load_dotenv()

llm =  ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 使用memory组件保存对话历史
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)




def polish_question(raw_question):
    system_message = SystemMessage(content="你是一个中文的写作助手，主要工作是是重写来自调查问卷的问题，使其更像自然对话中说出的话。")
    human_message_prompt = (
        "请将以下医疗问卷中的问题改写为自然对话形式，使其更适合通过聊天进行问答。改写后的问题应简单、亲切，并与患者日常生活相关，帮助患者在轻松的氛围中提供真实的回答。\n"
        "如果问题中有选项，你不应该把选项也包含在改写后的问题中，因为你需要尽量让你改写后的问题更像是在与人聊天时说出的话，而不是一道来自问卷的问题。\n"
        "以下是需要重写的问题：\n"
        f"{raw_question}\n\n"
        "输出内容限制：你的输出内容应该只包含你重写后的问题，不应该包含原问题以及其他任何内容"
    )
    human_message = HumanMessage(content=human_message_prompt)
    messages = [system_message, human_message]
    result = llm.invoke(messages)
    return result.content


def answer_is_valid(question, answer):
    system_message = SystemMessage(content="你是一个中文的意图判断器，主要工作是是判断用户的输入是否是在回答询问用户的问题。")
    human_message_prompt = (
        "刚刚问了用户以下问题：\n"
        f"{question}\n"
        "请判断以下用户的输入是否回答了上面的问题。用户的输入如下：\n"
        f"{answer}\n"
        "你的回答只有两种，每种只包含一个汉字：1. 是 2. 否。\n"
        "如果用户输入的内容与问题无关，或者不包含足以回答这个问题的有效信息，也回答否。\n"
        "如果原问题是没有选项的简答题，那么你对用户回答有效性的判断应该更加宽松，只要用户的回答不是完全离题。\n"
        "输出内容限制：你的输出内容应该只包含你的一个字的判断结果，不应该包含原问题、原回答以及其他任何内容。"
    )
    human_message = HumanMessage(content=human_message_prompt)
    messages = [system_message, human_message]
    result = llm.invoke(messages)
    if result.content == "是":
        return True
    return False

def analyze_and_rewrite_answer(raw_question, answer):
    system_message = SystemMessage(content="你是一个中文的写作助手，主要工作是是重写用户的回答，使其变成对于原问题的规范回答。")
    human_message_prompt = (
        "刚刚问了用户以下问题：\n"
        f"{raw_question}\n"
        "如果上面的问题是拥有选项的选择题或判断题，则把用户的回答总结成选项，这时你的输出应该只包含一个代表选项的英文字母，A B C D\n"
        f"如果上面的问题是没有选项的简答题，那么你只需要直接输出用户的原回答：{answer}\n"
        "你需要处理的用户回答如下：\n"
        f"{answer}\n\n"
        "输出内容限制：你的输出内容应该只包含你规范后的回答，不应该包含原回答或你的思考过程以及其他任何内容"
    )
    human_message = HumanMessage(content=human_message_prompt)
    messages = [system_message, human_message]
    result = llm.invoke(messages)
    return result.content

def guide_chat(question, answer):
    system_message = SystemMessage(content="你是一个中文的聊天助手，主要工作是在用户回答不当时，重新引导用户回答问题。")
    human_message_prompt = (
        "刚刚问了用户以下问题：\n"
        f"{question}\n"
        "用户的回答如下：\n"
        f"{answer}\n"
        "由于这里用户的回答不够详细或者不符合问题的要求，你需要组织语言引导用户来回答问题。\n"
        "如果用户在输入中提出了其他的问题，你应该引导用户回答原问题，而不是回答用户提出的问题。\n"
        "输出内容限制：你的输出内容应该只包含你引导用户继续回答下一个问题的内容，不应该包含用户的回答、原问题以及其他任何内容。"
    )
    human_message = HumanMessage(content=human_message_prompt)
    messages = [system_message, human_message]
    result = llm.invoke(messages)
    return result.content

def give_diet_suggestion(disease):
    diet_knowledge = query_in_vectorstore("糖尿病饮食建议")
    system_message = SystemMessage(content="你是一个营养师，主要工作是是根据用户的回答给出饮食建议。")
    human_message_prompt = (
        f"你需要给出一个给{disease}患者的饮食建议\n"
        "你的回答应该包含以下内容：\n"
        f"1. 你的饮食建议应该是针对{disease}患者的，应该包含一些糖尿病患者的饮食禁忌和注意事项。\n"
        "2. 你的饮食建议应该是简单明了的，不应该包含过于专业的医学术语。\n"
        "你的回答可以参考下面提供的相关信息：\n"
        f"{diet_knowledge}\n"
        "输出内容限制：你的输出内容应该只包含你的饮食建议，不应该包含用户的回答或你的思考过程以及其他任何内容。"
    )
    human_message = HumanMessage(content=human_message_prompt)
    messages = [system_message, human_message]
    result = llm.invoke(messages)
    #return result.content
    print(result.content)

# # 定义工具
# def fill_questionnaire_from_anwser(questionnaire, question, answer):
#     """根据用户的回答填写问卷"""

# tools = [
#     Tool(
#         name="questionnaire_filler",
#         func=fill_questionnaire_from_anwser,
#         description="当用户回答了刚刚问的问题时，用于根据用户的回答填写问卷",
#     ),
# ]


# # 创建react代理
# prompt = hub.pull("hwchase17/react")
# agent = create_react_agent(
#     llm=llm,
#     tools=tools,
#     prompt=prompt,
#     stop_sequence=True,
# )
# agent_executor = AgentExecutor.from_agent_and_tools(
#     agent=agent, # type: ignore
#     tools=tools,
#     verbose=True,
#     memory=memory,
# )

# 设置system message 
# system_message = ""
# memory.chat_memory.add_message(SystemMessage(content=system_message))



# 主要工作流程
# initial_message = "医生助理: 您好，我是XX医院的医生助理，为了帮助您更好地康复，我们需要向您了解一下您的康复情况，可以吗？"
# print(initial_message)
# user_input = input(f"{patient['name']}: ")
# system_message = SystemMessage(content=f"你是一个意图判断器，根据用户的输入判断用户对于以下问题回答是肯定还是否定。问题如下：\n{initial_message}.\n你的回答只有两种，每种只包含一个汉字：1. 是 2. 否。\n如果用户的回答与问题无关，也回答否。")
# human_message = HumanMessage(content=user_input)
# messages = [system_message, human_message]
# result = llm.invoke(messages)
# if result.content == "否":
#     sys.exit("好的，祝您生活愉快！")

# # 问卷循环
# while diabetes_questionnaire.have_questions_left():
#     # 获取下一个问题
#     next_question = diabetes_questionnaire.get_next_question()
#     index = next_question[0]
#     raw_question = next_question[1]
#     polished_question = polish_question(raw_question)

#     # 与患者对话
#     print("\n医生助理: ", polished_question)
#     memory.chat_memory.add_message(ToolMessage(content=next_question, tool_call_id="question_tool"))

#     user_input = input(f"{patient['name']}: ")

#     while True:
#         print("***** debug info *****")
#         print(f"raw_question: {raw_question}")
#         print(f"user_input: {user_input}")
#         print("***** debug info *****")
#         if answer_is_valid(raw_question, user_input):
#             break
#         else:
#             user_input = guide_chat(polished_question, user_input)
#             print("\n医生助理: ", user_input)
#             user_input = input(f"{patient['name']}: ")

#     memory.chat_memory.add_message(HumanMessage(content=user_input))

#     # 回答问题
#     answer = analyze_and_rewrite_answer(raw_question, user_input)
#     print("***** debug info *****")
#     print(f"raw_question: {raw_question}")
#     print(f"answer: {answer}")
#     print("***** debug info *****")
#     diabetes_questionnaire.set_answer(index, answer)

# diabetes_questionnaire.print_all_questions_and_answers()

give_diet_suggestion(patient["disease"])

# 打印对话历史
for message in memory.chat_memory.messages:
    print(f"{message.type}: {message.content}")