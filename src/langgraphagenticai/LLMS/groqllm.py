from langchain_groq import ChatGroq

def get_llm(api_key: str, model_id: str):
    if not api_key or not api_key.strip():
        raise ValueError("Groq API key is required")
    return ChatGroq(api_key=api_key.strip(), model=model_id, temperature=0, max_retries=2)
