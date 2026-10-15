from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PDF_DIR = DATA / "pdfs"
CHROMA_DIR = DATA / "chroma"
ANSWERS_FILE = DATA / "answers.jsonl"
FEEDBACK_FILE = DATA / "feedback.jsonl"
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen/qwen3.8-27b"]
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "science_pdf_collection"
MAX_REWRITES = 2
