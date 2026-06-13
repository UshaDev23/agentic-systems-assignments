from langchain_openai import ChatOpenAI
import os
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent



orders_db = {
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

@tool
def get_order_status(order_id: str) -> str:
    """
    Get the status of an order by its ID.
    Use this tool when the user asks about the order status for a specific order_id.
    """
    order_data = orders_db.get(order_id)
    if not order_data:
        return f"Order {order_id} not found."
    else:
        return order_data['status']
    
@tool
def estimate_delivery_timeline(order_id: str) -> str:
    """
    Estimate the delivery time for the given order_id
    Use this tool when the user asks about the estimated delivery time for a specific order_id.
    """
    order_data = orders_db.get(order_id)
    if order_data:
        if order_data["status"] == "Shipped":
            return f"Order for {order_id} will be delivered in {order_data['delivery_days']}."
        elif order_data["status"] == "Delivered":
            return f"Order {order_id} has already been delivered."
        else:
            return f"Order {order_id} is not shipped yet, so delivery time cannot be estimated."
    else:
        return f"Order Not Found."


@tool
def calculate_refund_amount(order_id: str) -> str:
    """
    Calculate the refund amount of the given order_id
    Use this tool when the user asks about the refund amount for a specific order_id.
    """
    order_data = orders_db.get(order_id)
    if not order_data:
        return f"Order {order_id} not found."

    if order_data['status'] == "Cancelled":
        return f"Refund amount for order {order_id} is ₹{order_data['amount']}."

    return f"Order {order_id} is not cancelled, so no refund is applicable."
    
tools =[
    get_order_status,
    estimate_delivery_timeline,
    calculate_refund_amount
]

llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                    You are an Order Support Assistant.

                    Your job is to help customers with order-related queries by selecting and using the appropriate tool when needed.

                    ## Available Tools

                    ### 1. get_order_status(order_id)
                    Use this tool when the user wants to know:
                    - Current order status
                    - Whether an order is shipped, delivered, cancelled, pending, or processing
                    - General order tracking information

                    Examples:
                    - What is the status of ORD-101?
                    - Has my order been shipped?
                    - Track order ORD-105

                    ### 2. estimate_delivery_timeline(order_id)
                    Use this tool when the user asks:
                    - When the order will arrive
                    - Delivery ETA
                    - Delivery timeline
                    - How many days are remaining

                    Examples:
                    - When will ORD-101 arrive?
                    - How long will delivery take?
                    - Estimated delivery for ORD-102?

                    ### 3. calculate_refund_amount(order_id)
                    Use this tool when the user asks:
                    - Refund amount
                    - Refund eligibility
                    - How much money will be refunded
                    - Refund after cancellation

                    Examples:
                    - What refund will I receive for ORD-103?
                    - Calculate refund for my cancelled order.
                    - How much money will I get back?

                    ## Tool Selection Rules

                    1. If the user asks about order status, call get_order_status.
                    2. If the user asks about delivery time, call get_estimated_delivery_time.
                    3. If the user asks about refunds, call calculate_refund_amount.
                    4. If the user asks multiple questions, call all required tools.
                    5. Never guess order information.
                    6. If an order ID is missing, ask the user to provide it.
                    7. Always provide a clear and concise response based on tool outputs.

                    ## Examples

                    User: What is the status of ORD-101?
                    Action: get_order_status("ORD-101")

                    User: When will ORD-101 be delivered?
                    Action: get_estimated_delivery_time("ORD-101")

                    User: What refund amount will I get for ORD-103?
                    Action: calculate_refund_amount("ORD-103")

                    User: Is ORD-101 shipped and when will it arrive?
                    Actions:
                    1. get_order_status("ORD-101")
                    2. get_estimated_delivery_time("ORD-101")

                    User: My order was cancelled. How much refund will I get?
                    If order ID is missing:
                    Ask the user for the order ID.

                    Respond to the user's query using the appropriate tool(s).


                    IMPORTANT:
                    - Do not answer from your own knowledge.
                    - Use tools whenever order information is requested.
                    - Never fabricate order status, delivery estimates, or refund amounts.
                    - If the required information is unavailable, state that clearly.
                    - If multiple tools are needed, call them sequentially and combine the results into a single response.
                """
         
         ),
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
    max_iterations=3,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

test_queries = [

    # Single tool Query
    "What is the current status of order ORD-101?",
    # Multi Tool Query
    "Can you tell me the status of ORD-101 and when it is expected to be delivered?",
    # No Tool Query
    "What services can you help me with regarding orders?",
    # Invalid order Query
    "What is the status of order ORD-999?"
]

def ask_agent():
    for query in test_queries:
        response = agent_executor.invoke(
            {
                "input": query
            }
        )
        print(response)

ask_agent()
    




