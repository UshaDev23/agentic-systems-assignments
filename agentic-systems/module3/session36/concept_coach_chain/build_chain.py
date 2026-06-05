from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:0.6b"

def build_chain():
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
             """
                You are a beginner friendly assistant who explains REST APIs in a simple way.

                Rules:
                1. Use simple language and avoid technical jargon.
                2. Provide examples to illustrate concepts.
                3. Break down complex ideas into easy-to-understand steps.
                4. Do not add an introduction.
                5. Do not add a conclusion.
                """
            ),

            (
                "human",
                "Explain the concept of {topic} using an analogy from the {analogy_domain} domain."
            )
        ]
    )

    llm = ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_HOST,
        temperature=1
    )

    parser = StrOutputParser()

    chain = prompt | llm |parser

    return chain