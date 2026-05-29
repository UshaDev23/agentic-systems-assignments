from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:0.6b"

LESSON_BRIEFS = [
    {
        "topic": "SQL Indexes",
        "audience": "beginners",
        "tone": "simple",
        "limit": 120
    },
     {
        "topic": "FastAPI dependency injection",
        "audience": "intermediate developers",
        "tone": "technical",
        "limit": 180
    },
     {
        "topic": "LangChain PromptTemplate",
        "audience": "product managers",
        "tone": "friendly",
        "limit": 100
    }
]
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
                "Explain {topic} to {audience} in {tone} tone and stay within {limit} words."
            )
        ]
    )

    llm = ChatOllama(
        model = MODEL_NAME,
        base_url = OLLAMA_HOST,
        temperature = 1
    )

    parser = StrOutputParser()
    chain = prompt | llm | parser

    return chain

chain = build_chain()

def validate_brief(brief):
    if not brief.get("topic"):
        raise ValueError("Topic is required in the lesson brief.")
    if not brief.get("audience"):
        raise ValueError("Audience is required in the lesson brief.")
    if not brief.get("tone"):
         raise ValueError("Tone is required in the lesson brief.")
    if type(brief.get("limit")) is not int:
        raise ValueError("Limit should be integet always in the lesson brief.")
    result = chain.invoke(brief)
    return result
    

for lesson in LESSON_BRIEFS:
    output = validate_brief(lesson)
    print(output)
