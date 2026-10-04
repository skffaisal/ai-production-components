# uv run python -c "from dotenv import load_dotenv; load_dotenv(); from langfuse import get_client; print(get_client().auth_check())"

# this is a check if langfuse is reachable 


from langfuse import get_client, observe


@observe(name="hello-world")
def hello_world() -> str:
    return "Hello from Langfuse"


if __name__ == "__main__":
    result = hello_world()
    print(result)

    langfuse = get_client() 
    langfuse.flush()