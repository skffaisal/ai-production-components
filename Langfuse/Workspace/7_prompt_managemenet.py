"""
In the langfuse UI, first go and create a prompt in prompt management
"""
from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

prompt = langfuse.get_prompt(
    "qwen-chat-system",
    label="production",
)

print("Prompt version:", prompt.version)
print("Prompt labels:", prompt.labels)
print("Prompt content:")
print(prompt.prompt)

langfuse.flush()