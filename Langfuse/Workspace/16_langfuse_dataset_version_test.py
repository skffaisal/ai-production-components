
from datetime import datetime, timezone

from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()
langfuse = get_client()

dataset_name = "evaluation/qwen-chat-regression"


version_timestamp = datetime.fromisoformat(
    "2026-10-15T09:57:52.629Z"
)


historical_dataset = langfuse.get_dataset(
    name=dataset_name,
    version=version_timestamp,
)

latest_dataset = langfuse.get_dataset(name=dataset_name)

print(f"Historical version items: {len(historical_dataset.items)}")
print(f"Latest version items: {len(latest_dataset.items)}")
