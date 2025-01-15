from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# 通义千问
model = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

chat_history = [
    SystemMessage(content="你是一个智能问答助手，可以回答我任何问题。你的回答注意尽量简短，除非我特别要求你给出详细的回答，你的回答都应该在5句话以内。")
]

print("Starting to chat with llm...")
while True:
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=user_input)) 

    result = model.invoke(chat_history)
    print(f"\nAI: {result.content}")
    chat_history.append(AIMessage(content=result.content))