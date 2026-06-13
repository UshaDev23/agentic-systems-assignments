from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage
import os

orders = {
    "ORD-101": {
        "status": "Shipped",
        "city": "Delhi",
        "amount": 2500,
        "delivery_days": 2
    },
    "ORD-102": {
        "status": "Delivered",
        "city": "Mumbai",
        "amount": 1800,
        "delivery_days": None
    },
    "ORD-103": {
        "status": "Cancelled",
        "city": "Bangalore",
        "amount": 3200,
        "delivery_days": None
    },
    "ORD-104": {
        "status": "Pending",
        "city": "Chennai",
        "amount": 1500,
        "delivery_days": None
    },
    "ORD-105": {
        "status": "Processing",
        "city": "Pune",
        "amount": 4200,
        "delivery_days": 5
    },
    "ORD-106": {
        "status": "Shipped",
        "city": "Hyderabad",
        "amount": 2750,
        "delivery_days": 4
    },
    "ORD-107": {
        "status": "Delivered",
        "city": "Kolkata",
        "amount": 5100,
        "delivery_days": None
    }
}


SYSTEM_PROMPT = """
                    You are an Order Support Assistant.

                    You have access to the following tool:

                    get_order_status(order_id)
                    - Retrieves the current status of an order.
                    - Use this tool whenever the user asks about the status of an order.

                    Conversation Rules:

                    1. Use the get_order_status tool whenever order status information is requested.
                    2. Never invent order information. Always use the tool.
                    3. Pay attention to the conversation history and previous assistant responses.
                    4. Remember the most recently discussed order_id from the conversation.
                    5. If the user refers to an order indirectly using phrases such as:
                    - "that order"
                    - "this order"
                    - "the same order"
                    - "it"
                    - "its status"
                    then assume they are referring to the most recently discussed order unless the user specifies a different order_id.
                    6. If no order_id can be determined from either the current message or the conversation history, ask the user to provide the order_id.
                    7. When responding, provide concise and helpful answers.

                    Examples:

                    Turn 1:
                    User: What is the status of ORD-101?
                    Action: Call get_order_status("ORD-101")

                    Assistant: Order ORD-101 is currently Shipped.

                    Turn 2:
                    User: Can you check it again?
                    Action: Call get_order_status("ORD-101")

                    Assistant: Order ORD-101 is currently Shipped.

                    Turn 1:
                    User: Check ORD-105.
                    Action: Call get_order_status("ORD-105")

                    Assistant: Order ORD-105 is currently Processing.

                    Turn 2:
                    User: Has that order been delivered?
                    Action: Call get_order_status("ORD-105")

                    Assistant: Order ORD-105 is currently Processing and has not yet been delivered.

                    Always use conversation context to resolve references before asking the user for an order_id.
                """


@tool
def get_order_status(order_id: str) -> str:
    """
    Get the status of an order by its ID.
    Use this tool when the user asks about the order status for a specific order_id.
    """
    order_data = orders.get(order_id)
    if not order_data:
        return f"Order {order_id} not found."
    else:
        return order_data['status']
    
tools = [get_order_status]

llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),

        MessagesPlaceholder(variable_name="chat_history", optional=True),

        ("human", "{input}"),

        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)
 
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

chat_history = []

def ask_agent(user_input):
    reponse = agent_executor.invoke(
        {
            "input": user_input,
            "chat_history": chat_history
        }
    )
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=reponse['output']))

    return reponse['output']


print("Turn -01")
user_input = "Hi, my order id ORD-102"
print("User Input: ", user_input)
print("AI response", ask_agent(user_input))

print("================================")

print("Turn -02")
user_input = "What is the status of it?"
print("User Input: ", user_input)
print("AI response", ask_agent(user_input))
print("===============================")

print(len(chat_history))

    

