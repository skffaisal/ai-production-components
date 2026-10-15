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
    # max_tokens=100,
    reasoning_effort="none",
)


# ---------------------------------------------------------
# Chain
# ---------------------------------------------------------

chain = langchain_prompt | model


# ---------------------------------------------------------
# Execute
# ---------------------------------------------------------


def response_non_empty(output: object) -> tuple[bool, str]:
    """Check whether the model produced a non-empty text response."""

    if isinstance(output, str):
        text = output
    elif isinstance(output, list):
        text = " ".join(
            item if isinstance(item, str)
            else item.get("text", "")
            if isinstance(item, dict)
            else ""
            for item in output
        )
    else:
        text = ""

    if not text.strip():
        return False, "Response is missing or empty."

    return True, "Response contains non-whitespace content."


if __name__ == "__main__":
    langfuse_handler = CallbackHandler()

    with langfuse.start_as_current_observation(
        as_type="span",
        name="MANAGED_PROMPT_QA",
    ) as request_span:

        response = chain.invoke(
            {"question": "Explain the faradays law"},
            config={
                "callbacks": [langfuse_handler],
                "run_name": "MANAGED_PROMPT_QA",
            },
        )

        print("\nModel response:")
        print(response.content)

        passed, comment = response_non_empty(response.content)

        request_span.score_trace(
            name="response_non_empty",
            value=1 if passed else 0,
            data_type="BOOLEAN",
            comment=comment,
        )

        print(f"\nresponse_non_empty={passed}")
        print(f"comment={comment}")

    langfuse.flush()
