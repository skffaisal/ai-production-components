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

langfuse_prompt = langfuse.get_prompt(
    "qwen-chat-system",
    label="production",
    type="chat",
)

print(f"Langfuse prompt version: {langfuse_prompt.version}")
print(f"Langfuse prompt labels: {langfuse_prompt.labels}")


# ---------------------------------------------------------
# Convert Langfuse prompt → LangChain prompt
# ---------------------------------------------------------

langchain_prompt = ChatPromptTemplate(
    langfuse_prompt.get_langchain_prompt(),
    metadata={
        "langfuse_prompt": langfuse_prompt,
    },
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
        {},
        config={
            "callbacks": [langfuse_handler],
            "run_name": "MANAGED_PROMPT_QA",
        },
    )

    print("\nModel response:")
    print(response.content)

    langfuse.flush()