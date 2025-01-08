import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
# from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.embeddings.dashscope import DashScopeEmbeddings 

### 全局替换sqlite3为新版本 ###
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# 设置文件路径
current_dir = os.path.dirname(os.path.abspath(__file__)) # abspath获取当前文件的绝对路径，再用dirname获取目录的路径 -> 当前工作路径
file_path = os.path.join(current_dir, "book", "chapters", "1.txt")
persistent_directory = os.path.join(current_dir, "db", "chroma_db1_metadata")


def query_in_vectorstore(query):
    client = ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    embeddings = DashScopeEmbeddings(client=client, model="text-embedding-v2") # 如果不传入client，会自动创建一个client，能够正常运行，不过可能会报错

    # 初始化一个Chroma对象用于检索
    db_query = Chroma(embedding_function=embeddings, persist_directory=persistent_directory)

    retriever = db_query.as_retriever(
        search_type="similarity",   # similarity方法只是按相似度排序，然后返回相似度最高的k个chunk，不会有阈值
        search_kwargs={"k": 3}, 
    )

    relevant_docs = retriever.invoke(query)
    
    # 将检索到的文档内容组合成一个字符串
    docs_content = " ".join([doc.page_content for doc in relevant_docs]) 
    return docs_content