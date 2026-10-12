import os

from dotenv import load_dotenv
from langfuse import get_client

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

# Simulate Langfuse being unreachable.
# This override affects only this Python process.
os.environ["LANGFUSE_BASE_URL"] = "http://127.0.0.1:9"

langfuse = get_client()


# ---------------------------------------------------------
# Local fallback prompt
# ---------------------------------------------------------

fallback_prompt = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI assistant.\n\n"
            "Answer the user's question clearly and concisely.\n"
            "If you are unsure about something, say so "
            "rather than inventing information."
        ),
    },
    {
        "role": "user",
        "content": "{{question}}",
    },
]


# ---------------------------------------------------------
# Fetch managed prompt, with fallback
# ---------------------------------------------------------

prompt = langfuse.get_prompt(
    "qwen-chat-system",
    label="production",
    type="chat",
    fallback=fallback_prompt,
    max_retries=0,
    fetch_timeout_seconds=1000,
)

print("Using fallback:", prompt.is_fallback)

if not prompt.is_fallback:
    raise RuntimeError(
        "Expected fallback prompt, but a managed prompt was returned."
    )


# ---------------------------------------------------------
# Build LangChain prompt
# ---------------------------------------------------------

langchain_prompt = ChatPromptTemplate(
    prompt.get_langchain_prompt(),
)


# ---------------------------------------------------------
# Groq / Qwen
# ---------------------------------------------------------

model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=0.2,
    max_tokens=100,
    reasoning_effort="none",
)

chain = langchain_prompt | model


# ---------------------------------------------------------
# Execute without Langfuse tracing
# ---------------------------------------------------------

response = chain.invoke(
    {
        "question": "Explain Python decorators in one sentence."
    }
)

print("\nModel response:")
print(response.content)