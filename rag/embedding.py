import os
from dotenv import load_dotenv

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.embeddings.dashscope import DashScopeEmbeddings 

### 全局替换sqlite3为新版本 ###
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# 设置文件路径
current_dir = os.path.dirname(os.path.abspath(__file__)) # abspath获取当前文件的绝对路径，再用dirname获取目录的路径 -> 当前工作路径
file_path = os.path.join(current_dir, "diet_info.txt")
persistent_directory = os.path.join(current_dir, "db")

# 文件加载
loader = TextLoader(file_path)
docs = loader.load()

# 文件分块
docs_chunks = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator="\n").split_documents(docs) # chunks还是以Document列表的形式返回的

# 创建embedding对象
from langchain_openai import ChatOpenAI
load_dotenv()
client = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
embeddings = DashScopeEmbeddings(client=client, model="text-embedding-v2") # 如果不传入client，会自动创建一个client，能够正常运行，不过可能会报错

# 初始化chroma向量数据库
db_init = Chroma.from_documents(docs_chunks, embeddings, persist_directory=persistent_directory)

    