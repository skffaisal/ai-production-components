# uv run python -c "from dotenv import load_dotenv; load_dotenv(); from langfuse import get_client; print(get_client().auth_check())"

# this is a check if langfuse is reachable 

# this is python SDK
from dotenv import load_dotenv
from langfuse import get_client, observe

load_dotenv()


@observe(name="hello-world") # The Langfuse SDK's observe decorator automatically creates an observation around the function and associates it with a trace
def hello_world() -> str:
    return "Hello from Langfuse"


if __name__ == "__main__":
    result = hello_world()
    print(result)

    langfuse = get_client()
    langfuse.flush()