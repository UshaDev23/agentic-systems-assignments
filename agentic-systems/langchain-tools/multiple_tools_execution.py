import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# fake order database for demo purpose
orders_db = {  # define in-memory dictionary as mock database
    "ORD101": {"status": "shipped", "city": "Delhi", "amount": 2500, "delivery_days": 2},  # sample shipped order
    "ORD102": {"status": "cancelled", "city": "Bangalore", "amount": 1800, "delivery_days": 0},  # sample cancelled order
    "ORD103": {"status": "delivered", "city": "Mumbai", "amount": 3200, "delivery_days": 0},  # sample delivered order
}

@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a specific order ID.""" 
    order_data = orders_db.get(order_id)
    if not order_data:
        return f"No order found for order ID {order_id}."
    return (
        f"Order {order_id} is currently {order_data['status']} "  # include current order status
        f"for {order_data['city']} and amount is {order_data['amount']}."  # include city and amount
    )

@tool
def calculate_refund_amount(order_id: str) -> str:
    """Calculate refund-related response for a specific order ID."""
    order_data = orders_db.get(order_id)
    if not order_data:
        return f"No order found for order ID {order_id}."
    if order_data["status"] == "delivered":
        return (  # return policy-oriented message
            f"Order {order_id} is delivered. Refund eligibility depends on product policy."
        )
    if order_data["status"] == "cancelled":  # if cancelled order
        return f"Refund amount for order {order_id} is {order_data['amount']}."  # full refund case
    
    return (  # fallback for shipped/in-transit states
        f"Order {order_id} is shipped. Refund cannot be finalized at this stage."
    )


@tool
def estimate_delivery_timeline(order_id: str) -> str:
    """Estimate delivery timeline for a specific order ID."""
    order_data = orders_db.get(order_id)
    if not order_data:
        return f"No order found for order ID {order_id}."
    
    if order_data["status"] == "shipped":
        return (  # return ETA message
            f"Order {order_id} is shipped and expected in {order_data['delivery_days']} days."
        ) 
    if order_data["status"] == "delivered":  # if order already delivered
        return f"Order {order_id} has already been delivered."  # delivered response
    if order_data["status"] == "cancelled":  # if order cancelled
        return f"Order {order_id} is cancelled, so no delivery timeline exists."  # cancelled response
    return f"Delivery status for order {order_id} is currently unavailable."  # handle unknown status
    

tools = [get_order_status, calculate_refund_amount, estimate_delivery_timeline]

llm = ChatOpenAI(
    model="gpt-5.2",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful e-commerce support assistant. Use tools only when required."
        ),
        (
            "human",
            "{input}"
        ),
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
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

user_query = "For order ORD102, check status, delivery estimate, and refund amount."  # sample multi-tool query
result = agent_executor.invoke({"input":user_query})
print("Final Output:", result["output"])