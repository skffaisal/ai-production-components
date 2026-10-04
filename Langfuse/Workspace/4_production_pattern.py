# production pattern
'''
We've now established the production hierarchy:

Trace
  └── Application Span
       ├── Application Span
       └── Framework Chain
            ├── Prompt
            └── Generation

This is useful because when we eventually have something like:

AI_REQUEST
├── INPUT_VALIDATION
├── PII_GUARDRAIL
├── RETRIEVAL
├── RERANKING
├── LLM_GENERATION
├── TOOL_CALL
└── OUTPUT_GUARDRAIL
'''

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

    with langfuse.start_as_current_observation(
        as_type="span",
        name="AI_REQUEST",
    ) as root_span:

        with propagate_attributes(
            trace_name="ai-error-tracing",
            user_id="user-error-test-001",
            session_id="session-error-test-001",
            tags=[
                "langfuse-training",
                "error-tracing",
                "pipeline-test",
            ],
            metadata={
                "application": "langfuse-training",
                "environment": "local",
                "test_type": "error-tracing",
            },
        ):
            question = "What is a Python decorator?"

            # Application-level input processing
            with langfuse.start_as_current_observation(
                as_type="span",
                name="INPUT_PROCESSING",
            ) as input_span:

                processed_question = question.strip()

                input_span.update(
                    input={
                        "raw_question": question,
                    },
                    output={
                        "processed_question": processed_question,
                    },
                )

            # LangChain workflow
            response = chain.invoke(
                {
                    "question": processed_question,
                },
                config={
                    "callbacks": [langfuse_handler],
                    "run_name": "Q_AND_A_CHAIN",
                },
            )

            root_span.update(
                output={
                    "answer": response.content,
                }
            )

    print(response.content)

    langfuse.flush()