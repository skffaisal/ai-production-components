# THis is Langchain framework 

import os

from dotenv import load_dotenv
from langfuse import get_client , propagate_attributes # for production identifiable attriburtes
from langfuse.langchain import CallbackHandler
from langchain.chat_models import init_chat_model

load_dotenv()
from langchain_core.prompts import ChatPromptTemplate

model = init_chat_model(
    model="qwen/qwen3.8-27b",
    model_provider="groq",
    temperature=0.2,
    max_tokens=100,
    reasoning_effort="none",
)
prompt = ChatPromptTemplate.from_template(
    "Answer the following question clearly and concisely:\n\n{question}"
)

chain = prompt | model

if __name__ == "__main__":
    langfuse = get_client()
    langfuse_handler = CallbackHandler()

    # -------------------------
    # TURN 1
    # -------------------------
    with langfuse.start_as_current_observation(
        as_type="span",
        name="AI_REQUEST",
    ):

        with propagate_attributes(
            trace_name="qwen-chat-new",
            user_id="user-123",
            session_id="session-001",
            tags=["langchain", "groq", "qwen"],
            metadata={
                "application": "langfuse-training",
                "environment": "local",
            },
        ):
            response = chain.invoke(
                {
                    "question": "What is a Python decorator?"
                },
                config={
                    "callbacks": [langfuse_handler],
                    "run_name": "Q_AND_A_CHAIN",
                },
            )

    # -------------------------
    # TURN 2
    # -------------------------
    with langfuse.start_as_current_observation(
        as_type="span",
        name="AI_REQUEST",
    ):

        with propagate_attributes(
            trace_name="qwen-chat-new",
            user_id="user-123",
            session_id="session-001",
            tags=["langchain", "groq", "qwen"],
            metadata={
                "application": "langfuse-training",
                "environment": "local",
            },
        ):
            response = chain.invoke(
                {
                    "question": "Why are decorators useful?"
                },
                config={
                    "callbacks": [langfuse_handler],
                    "run_name": "Q_AND_A_CHAIN",
                },
            )

    print(response.content)

    langfuse.flush()