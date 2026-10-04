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

    # Langfuse callback for LangChain tracing
    langfuse_handler = CallbackHandler()

    with langfuse.start_as_current_observation(
    as_type="span",
    name="AI_REQUEST",
    ) as root_span:

        with propagate_attributes(
            trace_name="qwen-chat-new", # identifies the overall trace
            user_id="user-1234",
            session_id="session-002",
            tags=["cost","added"],
            metadata={
                "application": "langfuse-training",
                "environment": "local",
            },
            ):
                response = chain.invoke(
                    "What is a chain in langchain?",
                    config={
                        "callbacks": [langfuse_handler],
                        "run_name": "Q_AND_A_CHAIN", # identifies the Generation observation
                        },
                    )
    # print("\n=== USAGE METADATA ===")
    # print(response.usage_metadata)

    # print("\n=== RESPONSE METADATA ===")
    # print(response.response_metadata)
    print(response.content)


    langfuse.flush() # used to manually force the Langfuse client to immediately send all buffered traces, observations, and metrics to the Langfuse API