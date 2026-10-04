# THis is Langchain framework 

import os

from dotenv import load_dotenv
from langfuse import get_client , propagate_attributes # for production identifiable attriburtes
from langfuse.langchain import CallbackHandler
from langchain.chat_models import init_chat_model

load_dotenv()


model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=0.2,
    max_tokens=100,
    reasoning_effort="none",
)


if __name__ == "__main__":
    langfuse = get_client()

    # Langfuse callback for LangChain tracing
    langfuse_handler = CallbackHandler()

    with propagate_attributes(
        trace_name="qwen-chat", # identifies the overall trace
        user_id="user-123",
        session_id="session-001",
        tags=["langchain", "groq", "qwen"],
        metadata={
            "application": "langfuse-training",
            "environment": "local",
        },
        ):
            response = model.invoke(
                "What is jev",
                config={
                    "callbacks": [langfuse_handler],
                    "run_name": "LLM_CALL_With_Attributes", # identifies the Generation observation
                    },
                )

    print(response.content)


    langfuse.flush() # used to manually force the Langfuse client to immediately send all buffered traces, observations, and metrics to the Langfuse API