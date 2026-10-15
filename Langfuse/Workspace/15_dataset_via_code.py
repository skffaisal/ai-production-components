from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

item = langfuse.create_dataset_item(
    dataset_name="evaluation/qwen-chat-regression",
    input={
        "question": "What is the difference between a list and a tuple in Python?"
    },
    expected_output={
        "answer": (
            "A list is mutable, so its elements can be changed after creation. "
            "A tuple is immutable, so its elements cannot be changed after creation."
        )
    },
    metadata={
        "source": "python-sdk-test",
        "category": "python-basics",
    },
)

langfuse.flush()

print(f"Dataset item created: {item.id}")
