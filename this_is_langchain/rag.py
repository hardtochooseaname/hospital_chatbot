import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.dashscope import DashScopeEmbeddings 

load_dotenv()
llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db_monkeyking")

embeddings = DashScopeEmbeddings(client=llm, model="text-embedding-v2")

db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)



# 封装rag链创建过程
def create_rag_chain(llm, retriever):
    # 这个提示词用于让 llm 根据chat history重写用户问题
    contextualize_q_system_prompt = (
        "根据聊天历史记录和最新的用户问题（该问题可能引用了聊天历史中的上下文），生成一个独立的问题，"
        "使其在没有聊天历史的情况下也能够被理解。"
        "不要回答问题，只需在需要时重新表述它，否则保持原样返回。"
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"), # 这里使用 MessagesPlaceholder 插入一个名为'chat_histroy'的占位符
            ("human", "{input}"),
        ]
    )

    # Create a history-aware retriever
    # step 1. 重写用户问题：把提示词给llm
    # setp 2. 使用重写的问题检索向量数据库
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 这是用于和llm对话的提示词，{context}在create_stuff_documents_chain时会自动被替换为传入的文档列表
    qa_system_prompt = (
        "你是一个负责问答任务的助手，使用以下检索到的上下文片段回答问题：\n"
        "{context}"  
        "如果你不能从上面的文本中得出答案，只需说明你不知道，你不能利用你自己的知识来回答。"
        "最多使用三句话，保持答案简洁。"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            ("human", "{input}"),
        ]
    )

    # 将传入的文档列表以stuff方式整合后，结合进提示词交给llm处理
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Core Part:
    # 用于将检索器（Retriever）和下游任务（如文档整合链、问答链）结合起来，创建一个从检索到回答的完整链
    # 1. 前面的检索器其实也是一个包含两个任务的复合链（根据历史重写用户问题 + 利用重写的问题检索文档）
    # 2. 后面的文档整合问答链也是一个复合链（文档整合 + llm问答）
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain


# 封装rag链调用过程
def call_rag_chain(rag_chain, query, chat_history):
    result = rag_chain.invoke({"input": query, "chat_history": chat_history})
    return result['answer']

def continual_chat():
    print("Start chatting with the AI! Type 'exit' to end the conversation.")
    chat_history = []  
    rag_chain = create_rag_chain(llm, retriever)
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        
        result = call_rag_chain(rag_chain, query, chat_history)
        print(f"AI: {result}")
        
        chat_history.append(HumanMessage(content=query))
        chat_history.append(SystemMessage(content=result))


if __name__ == "__main__":
    continual_chat()
