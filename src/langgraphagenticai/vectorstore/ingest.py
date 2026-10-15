import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import warnings
from pypdf.errors import PdfReadWarning

# Suppress specific PyPDF warnings
warnings.filterwarnings("ignore", category=PdfReadWarning)

from src.langgraphagenticai.config import PDF_DIR, CHROMA_DIR, COLLECTION
from src.langgraphagenticai.vectorstore.store import embeddings


def main():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(PDF_DIR.glob("*.pdf"))
    if not paths:
        raise SystemExit(f"Put at least one PDF in {PDF_DIR}")
    docs = []
    for path in paths:
        for doc in PyPDFLoader(str(path)).load():
            doc.metadata["source_file"] = path.name
            docs.append(doc)
    chunks = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150).split_documents(docs)

    if CHROMA_DIR.exists(): 
        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    Chroma.from_documents(chunks, embeddings(),
                           collection_name=COLLECTION,
                             persist_directory=str(CHROMA_DIR))
    
    print(f"Indexed {len(paths)} PDF(s), {len(chunks)} chunks")
if __name__ == "__main__": 
    main()
