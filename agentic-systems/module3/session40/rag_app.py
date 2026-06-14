from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from pathlib import Path
import os

DATA_DIRECTORY = Path("documents")
CHROMA_DIRECTORY = Path("chromadb")
COLLECTION_NAME = "hostel_policy_docs"
EMBEDDING_MODEL = "text-embedding-3-small"

llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIRECTORY)
)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful hostel information assistant.

            Answer the user's question using ONLY the retrieved context.

            Guardrails:
            1. Use only the information present in the retrieved context.
            2. Do not use prior knowledge.
            3. If the answer cannot be found in the context, respond exactly:
            "I don't know based on the provided documents."
            4. When possible, mention the source file name used to answer.
            5. Keep answers concise and factual.
            
            Retrieved Context:
            {context}
            """
        
        ),
        ("human", "{question}")
    ]
)

rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


if __name__ == "__main__":
    q1 = "What are the quiet hours on weekdays?"
    q2 = "What is the schlorship amount for hostel residents?"
    print("Question.No.1")
    r1 = rag_chain.invoke(q1)
    print("Retrieved Docs:", len(r1))
    print(r1)
    print("============================")
    print("Question.No.2")
    r2 = rag_chain.invoke(q2)
    print("Retrieved Docs:", len(r2))
    print(r2)