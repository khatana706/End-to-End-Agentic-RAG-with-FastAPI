from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.langgraphagenticai.config import CHROMA_DIR, COLLECTION, EMBEDDING_MODEL

def embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def vectorstore():
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(f"No Chroma index at {CHROMA_DIR}. Add PDF(s) to data/pdfs and run ingestion first.")
    return Chroma(collection_name=COLLECTION, persist_directory=str(CHROMA_DIR), embedding_function=embeddings())
  