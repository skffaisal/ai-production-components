
from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

# Copy this from an existing MANAGED_PROMPT_QA trace in Langfuse.
trace_id = "1b7e59210093cd777ce36efe556016f6"

# Simulate a user clicking thumbs-up.
langfuse.create_score(
    trace_id=trace_id,
    name="user_feedback",
    value=1,
    data_type="BOOLEAN",
    comment="User found the response helpful",
)

langfuse.flush()

print("User feedback score submitted.")
