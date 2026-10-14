from dotenv import load_dotenv

from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


# Load Workspace/.env
load_dotenv()

langfuse = get_client()


# Fetch the same production-managed prompt used by MANAGED_PROMPT_QA.
langfuse_prompt = langfuse.get_prompt(
    "qwen-chat-system",
    label="production",
    type="chat",
)

print(f"Langfuse prompt version: {langfuse_prompt.version}")
print(f"Langfuse prompt labels: {langfuse_prompt.labels}")


langchain_prompt = ChatPromptTemplate(
    langfuse_prompt.get_langchain_prompt(),
    metadata={"langfuse_prompt": langfuse_prompt},
)

model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=0.2,
    reasoning_effort="none",
)

chain = langchain_prompt | model


QUESTIONS = [
    "Explain Python decorators using a simple example.",
    "What is the difference between a Python list and a tuple?",
    "Explain Python generators and when you would use them.",
    "What is the difference between concurrency and parallelism?",
    "Explain database indexes and one trade-off they introduce.",
    "What is an API idempotency key, and why is it useful?",
    "Explain a database transaction and how rollback works.",
    "What is the difference between authentication and authorization?",
    "Explain Docker containers versus virtual machines.",
    "What does a reverse proxy do?",
    "What is Redis commonly used for in a backend system?",
    "What is the difference between SQL and NoSQL databases?",
    "How should a backend validate a JWT?",
    "What can happen when a database connection pool is exhausted?",
    "Explain caching and why cache invalidation can be difficult.",
    "What is a race condition? Give a simple example.",
    "Explain retry logic and exponential backoff.",
    "What is the difference between retrieval-augmented generation (RAG) and fine-tuning?",
    "Explain precision and recall in machine learning.",
    "Is Python always faster than C++? Explain your answer.",
]


def main() -> None:
    total = len(QUESTIONS)
    succeeded = 0
    failed = 0

    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\n[{index}/{total}] Question: {question}")

        try:
            # Create a handler for each invocation so each request's
            # LangChain observations are sent to Langfuse independently.
            handler = CallbackHandler()

            response = chain.invoke(
                {"question": question},
                config={
                    "callbacks": [handler],
                    "run_name": "MANAGED_PROMPT_QA",
                    "tags": ["phase3-evaluator-calibration"],
                    "metadata": {
                        "evaluation_batch": "phase3-20-questions",
                        "question_index": index,
                    },
                },
            )

            print("Response:")
            print(response.content)
            succeeded += 1

        except Exception as exc:
            failed += 1
            print(f"FAILED: {type(exc).__name__}: {exc}")

    # Flush buffered Langfuse events before the script exits.
    langfuse.flush()

    print("\nBatch complete.")
    print(f"Successful model calls: {succeeded}/{total}")
    print(f"Failed model calls: {failed}/{total}")
    print(
        "Next: in Langfuse, verify that the two judge scores exist for "
        "the new generations before sending the traces to human review."
    )


if __name__ == "__main__":
    main()
