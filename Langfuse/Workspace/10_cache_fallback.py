from dotenv import load_dotenv

from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# ---------------------------------------------------------
# Langfuse
# ---------------------------------------------------------

langfuse = get_client()


# ---------------------------------------------------------
# Fetch managed prompt
# ---------------------------------------------------------

# ---------------------------------------------------------
# Fetch managed prompt with fallback
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

langfuse_prompt = langfuse.get_prompt(
    "qwen-chat-system",
    label="production",
    type="chat",
    fallback=fallback_prompt,
)

if langfuse_prompt.is_fallback:
    print("WARNING: Using local fallback prompt.")
    prompt_metadata = {}
else:
    print(f"Prompt version: {langfuse_prompt.version}")
    print(f"Prompt labels: {langfuse_prompt.labels}")

    prompt_metadata = {
        "langfuse_prompt": langfuse_prompt,
    }

# ---------------------------------------------------------
# Convert Langfuse prompt → LangChain prompt
# ---------------------------------------------------------

langchain_prompt = ChatPromptTemplate(
    langfuse_prompt.get_langchain_prompt(),
    metadata=prompt_metadata,
)


# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=0.2,
    max_tokens=100,
    reasoning_effort="none",
)


# ---------------------------------------------------------
# Chain
# ---------------------------------------------------------

chain = langchain_prompt | model


# ---------------------------------------------------------
# Execute
# ---------------------------------------------------------

if __name__ == "__main__":

    langfuse_handler = CallbackHandler()

    response = chain.invoke(
        { "question": "Explain Python decorators using a simple example."},
        config={
            "callbacks": [langfuse_handler],
            "run_name": "MANAGED_PROMPT_QA",
        },
    )

    print("\nModel response:")
    print(response.content)

    langfuse.flush()