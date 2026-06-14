from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from pathlib import Path
import shutil
import os

COLLECTION_NAME = "helpdesk_policy_docs"
CHROMA_DIRECTORY = Path("chromadb")

# Policy Database
documents = [
    Document(
        page_content="Full refund within 7 days of enrollment if no live class attended. Partial refund within 30 days per program rules.",
        metadata={"source": "refund_policy.md"}
    ),
    Document(
        page_content="Minimum 75% attendance is required for certification and placement support.",
        metadata={"source": "attendance_policy.md"}
    ),
    Document(
        page_content="Students may request one batch change per cohort. Missing more than three classes without approved leave may delay batch change.",
        metadata={"source": "batch_change_policy.md"}
    )
]


# Fake Ticket Database
FAKE_TICKET_DATABASE = {
    "TKT-2001": "Refund request under review. Expected response in 2 working days.",
    "TKT-2002": "Batch change request approved. New batch starts next Monday.",
}


# Chunk the docs & store in db

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60
    )

split_docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME
    )

retriever = vector_store.as_retriever(
    search_type = "similarity",
    search_kwargs ={"k": 2}
)

course_policy_tool = create_retriever_tool(
    retriever=retriever,
    name="course_policy_tool",
    description=
        """
            Searches course policies and student support documentation.

            Use this tool when the user asks about:
            - Refund policy
            - Attendance requirements
            - Certification eligibility
            - Placement support eligibility
            - Batch change rules
            - Course guidelines
            - Student policies

            Do not use this tool for ticket status requests.
        """
    
)

@tool
def get_ticket_status(ticket_id: str):
    """
        Retrieves the status of a support ticket.

        Use this tool whenever:
        - The user asks for ticket status.
        - The user asks for updates on a ticket.
        - The user refers to a previously mentioned ticket using words like:
        'it', 'that ticket', 'this ticket', or 'my ticket'.

        Input:
            ticket_id: Support ticket identifier such as TKT-2001.

        Returns:
            Current ticket status.
    """
    ticket_status = FAKE_TICKET_DATABASE.get(ticket_id)
    if not ticket_status:
        return f"Ticket Not Found"
    else:
        return ticket_status
    
tools = [course_policy_tool, get_ticket_status]

llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

SYSTEM_PROMPT = """
                You are a Student Helpdesk Assistant.

                You have access to two tools:

                1. course_policy_tool
                - Retrieves information from course policy documents.
                - Use for refund, attendance, certification, placement support, and batch change questions.

                2. get_ticket_status(ticket_id)
                - Retrieves support ticket status.
                - Use whenever a ticket status is requested.

                Conversation Rules:

                1. Always use tools instead of guessing.
                2. Use course_policy_tool for policy-related questions.
                3. Use get_ticket_status for ticket-related questions.
                4. Pay attention to chat history.
                5. Remember the most recently mentioned ticket ID.
                6. If the user says:
                - it
                - this ticket
                - that ticket
                - my ticket
                then assume they mean the most recently mentioned ticket.
                7. If no ticket ID can be determined, ask the user for the ticket ID.
                8. Never invent policy information.
                9. Never invent ticket status.
                10. If information is unavailable, say so clearly.

                Examples:

                User: What is the refund policy?
                Action: course_policy_tool

                User: What is the status of TKT-2001?
                Action: get_ticket_status("TKT-2001")

                User: My ticket is TKT-2002
                Assistant: Noted. How can I help regarding ticket TKT-2002?

                User: What is the status of it?
                Action: get_ticket_status("TKT-2002")
        """

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", SYSTEM_PROMPT
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3
)

chat_history = []

def ask_agent(user_query: str) -> str:
    response = agent_executor.invoke(
        {
            "input": user_query,
            "chat_history": chat_history
        }
    )
    chat_history.append(HumanMessage(content=user_query))
    chat_history.append(AIMessage(content=response['output']))
    return response['output']

if __name__ == "__main__":
    q1 = "What is the refund policy in the first week?"
    print("Query.No.1: ", q1)
    print("Answer: ", ask_agent(q1))
    q2 = "What is the status of the ticket TKT-2001?"
    print("Query.No.2: ", q2)
    print("Answer: ", ask_agent(q2))
    q3 = "My support ticket is TKT-2002"
    print("Query.No.3: ", q3)
    print("Answer: ", ask_agent(q3))
    q4 = "What is the status of it?"
    print("Query.No.4: ", q4)
    print("Answer: ", ask_agent(q4))
    q5 = "Who won the IPL 2025?"
    print("Query.No.5: ", q5)
    print("Answer: ", ask_agent(q5))