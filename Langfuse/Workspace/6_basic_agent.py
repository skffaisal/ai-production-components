import os

from dotenv import load_dotenv

from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool


load_dotenv()


# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=1,
    reasoning_effort="high",
    reasoning_format="parsed",
)
"""
hidden  → don't return reasoning
raw     → reasoning appears inside content as <think>...</think>
parsed  → reasoning appears separately in message.reasoning
"""

# ---------------------------------------------------------
# Tool
# ---------------------------------------------------------

@tool
def calculator(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------

agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt=(
        "You are a helpful assistant. "
        "When addition is required, always use the calculator tool."
    ),
)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    langfuse = get_client()
    langfuse_handler = CallbackHandler()

    with propagate_attributes(
        trace_name="agent-tool-tracing",
        user_id="user-agent-test-001",
        session_id="session-agent-test-001",
        tags=[
            "langfuse-training",
            "agent",
            "tool-calling",
        ],
        metadata={
            "application": "langfuse-training",
            "environment": "local",
            "test_type": "agent-tool-tracing",
        },
    ):

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "what is 45+45", #  Who are you?
                    }
                ]
            },
            config={
                "callbacks": [langfuse_handler],
                "run_name": "CALCULATOR_AGENT",
            },
        )

    # Final assistant response
    print("\n=== FINAL RESPONSE ===")
    # print(result["messages"][-1].content)
    print(result)

    # Short-lived script: make sure queued Langfuse events are sent.
    langfuse.flush()
    