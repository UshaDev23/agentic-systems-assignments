from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import shutil

# 1. Document Creation
DATA_DIRECTORY = Path("documents")
CHROMA_DIRECTORY = Path("chromadb")
COLLECTION_NAME = "hostel_policy_docs"
EMBEDDING_MODEL = "text-embedding-3-small"

# 2. Document Loading
loader = DirectoryLoader(
    path=str(DATA_DIRECTORY),
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={
        "encoding" :"utf-8"
    }
)

doc_data = loader.load()

# 3. Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 400,
    chunk_overlap = 60,
    add_start_index = True
)

chunks = text_splitter.split_documents(doc_data)

# 4. Generate Embeddings & store to vector db
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
if CHROMA_DIRECTORY.exists():
    shutil.rmtree(CHROMA_DIRECTORY)

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIRECTORY)
)

ids = vector_store.add_documents(documents=chunks)
print(f"Documents loaded: {len(doc_data)}")
print(f"Chunks created: {len(chunks)}")