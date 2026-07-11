import json # Convert Python dicts to JSON strings for ToolMessage content
import os
from typing import Literal  # Restrict a field to fixed allowed strings

from langchain.chat_models import init_chat_model # Factory to create chat models by name
from langchain.tools import tool # Decorator that registers a function as a LangChain tool
from langchain.messages import ToolMessage # Message type that carries tool output back to the LLM
from pydantic import BaseModel, Field

API_KEY = os.environ.get("OPENAI_API_KEY")

ORDERS_DB = {
    "ORD1001": {
        "order_id": "ORD1001",
        "item": "Wireless Mouse",
        "status": "shipped",
        "payment_status": "paid",
        "eta_days": 2,
    },
    "ORD1002": {
        "order_id": "ORD1002",
        "item": "USB-C Cable",
        "status": "delivered",
        "payment_status": "paid",
        "eta_days": 0,
    },
}

POLICIES_DB = {
    "refund": "Refunds are allowed within 7 days of delivery for damaged or wrong products.",
    "shipping": "Standard shipping takes 3-5 business days. Express is available at checkout.",
    "warranty": "Electronics have a 12-month manufacturer warranty from delivery date.",
}

REFUND_TICKETS = {}  # Filled when create_refund_ticket succeeds

class OrderStatusInput(BaseModel):
    order_id: str = Field(
        description="Order Id which can be in the format ORD1001"
    )

class PolicyLookUpInput(BaseModel):
    topic: Literal["refund", "shipping", "warranty"] = Field(
        description="Policy topic. Must be refund, shipping, or warranty."
    )

class RefundTicketInput(BaseModel):
    order_id: str = Field(
        description="Order ID such as ORD1001."
    )
    reason: Literal["damaged", "late_delivery", "wrong_item"] = Field(
        description="Refund Reason"
    )
    customer_note: str = Field(
         default="",
        description="Short explanation from the customer."
    )

# Tool 1: Order Status
@tool(args_schema=OrderStatusInput)
def get_order_status(order_id: str) -> str:
    """Fetch order status, item details, payment status, and delivery ETA.
    Use only when the user asks about status, delivery, shipping, or ETA of a specific order."""
    order_data = ORDERS_DB.get(order_id)
    if not order_data:
        return json.dumps(
            {
                "ok": False,
                "error_type": "order not found",
                "message": f"No order found for the {order_id}"
            }
        )
    return json.dumps({
        "ok": True,
        "order": order_data
    })

# Tool 2: Policy LookUp
@tool(args_schema=PolicyLookUpInput)
def lookup_policy(topic : str):
    """Look up company policy for refund, shipping, or warranty.
    Use when the user asks about rules, eligibility, or timelines."""
    policy = POLICIES_DB.get(topic)
    return json.dumps({
        "ok": True,
        "topic": topic,
        "policy_text": policy
    })

# Tool 3: Create Refund Ticket
@tool(args_schema=RefundTicketInput)
def create_refund_ticket(order_id: str, reason: str, customer_note: str):
    """Create a refund ticket for an existing paid order.
    Use when the user wants to file a refund request."""
    order_data = ORDERS_DB.get(order_id)
    if not order_data:
        return json.dumps({
            "ok": False,
            "error_type": "Order Not Found",
            "message": f"No Order found for the id {order_id}"
        })
    
    if order_data.get("payment_status") != "paid":
        return json.dumps({
            "ok": False,
            "error_type": "Payment Not Completed",
            "message": (
                    f"Cannot create refund for {order_id} "
                    f"because payment_status is {order_data.get('payment_status')}."
                ),
        })
    ticket_id = f"RF-{order_id}-001"
    REFUND_TICKETS[ticket_id]={
        "ticket_id": ticket_id,
        "order_id": order_id,
        "reason": reason,
        "customer_note": customer_note,
        "status": "created",
    }
    return json.dumps(
        {
            "ok": True,
            "ticket_id": ticket_id,
            "message": "Refund ticket created successfully.",
        }
    )

# --- Register tools for bind_tools ---
tools = [get_order_status, lookup_policy, create_refund_ticket]
tools_by_name = {t.name for t in tools} # Fast lookup when executing tool_calls

# --- Create model and bind tools ---
MODEL_NAME = "gpt-4o-mini"
model = init_chat_model(MODEL_NAME, temperature=0)
model_with_tools = model.bind_tools(tools)

def execute_tool_call_safely(tool_call: dict) -> ToolMessage:
    """Run one model-emitted tool call; never crash the whole agent."""
    tool_name = tool_call.get("name") # Which tool the model chose
    tool_call_id = tool_call.get("id") # Id linking ToolMessage back to this call
    tool_args = tool_call.get("args", {}) # Arguments dict from the model

    selected_tool = tools_by_name.get(tool_call_id)
    if selected_tool is None:
        error_payload = {
            "ok": False,
            "error_type": "unknown_tool",
            "message": f"Tool '{tool_name}' is not available.",
        }
        return ToolMessage(
            content=json.dumps(error_payload),
            tool_call_id=tool_call_id
        )
    try:
        result = selected_tool.invoke(tool_args)
        return ToolMessage(content=str(result), tool_call_id=tool_call_id)  # Success path
    except Exception as exc:  # Convert exception into recoverable signal for the LLM
        error_payload = {
            "ok": False,
            "error_type": "tool_execution_error",
            "message": str(exc),
        }
        return ToolMessage(
            content=json.dumps(error_payload),
            tool_call_id=tool_call_id,
        )
    
def run_customer_support_agent(userquery: str, max_steps: int=5) -> str:
    """Manual tool-feedback loop until the model returns a final text answer."""
    messages =[
        {
            "role":"system",
            "content": (
                "You are a helpful customer support agent. "
                "Use tools when you need order data, policy data, or to create a refund ticket. "
                "If a tool returns an error, explain the issue clearly and ask for missing or corrected information."
            )
        },
         {
                "role": "user",
                "content": userquery
        }
    ]
    for step in range(1, max_steps + 1):  # Limit loops so the agent cannot run forever
        ai_message = model_with_tools.invoke(messages)  # Model may return text and/or tool_calls
        messages.append(ai_message)  # Keep full conversation history

        tool_calls = getattr(ai_message, "tool_calls", None) or []  # Safe access to tool_calls
        if not tool_calls:  # No tools requested → this content is the final answer
            print(f"Step {step}: final model response")
            return ai_message.content
        
        print(f"Step {step}: tool_calls = {tool_calls}")  # Debug trace like live class
        for tool_call in tool_calls:  # A single turn may request multiple tools
            tool_message = execute_tool_call_safely(tool_call)  # Run each tool safely
            messages.append(tool_message)  # Feed result back for the next model turn
    return "I could not complete the request within the allowed number of steps."  # Safety exit



if __name__ == "__main__":
    test_queries = [
        "Where is my order ORD1001?",
        "Can I get a refund if my item arrived damaged?",
        "Create a refund ticket for ORD1001 because the item is damaged.",
        "What is your refund policy?",
        "Tell me a joke about databases.",
    ]
    for query in test_queries:
        print("\n" + "=" * 60)
        print("Query:", query)
        final_answer = run_customer_support_agent(query)  # Run agent for each query
        print("Final answer:", final_answer)