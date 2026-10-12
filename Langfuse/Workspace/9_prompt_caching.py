# keep this file running, and change the other prompt version to production
# The SDK continues serving Version 1 from its cache while it refreshes the prompt in the background. Once that refresh completes, subsequent fetches receive Version 2.
import time

from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

try:
    while True:
        prompt = langfuse.get_prompt(
            "qwen-chat-system",
            label="production",
            type="chat",
            cache_ttl_seconds=15,  # Short TTL for this demonstration
        )

        print(
            f"Fetched prompt version: {prompt.version} | "
            f"Labels: {prompt.labels}"
        )

        time.sleep(5)

except KeyboardInterrupt:
    print("\nCache test stopped.")