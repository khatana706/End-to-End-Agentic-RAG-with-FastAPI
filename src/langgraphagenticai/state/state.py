from typing import Any, TypedDict
class RAGState(TypedDict, total=False):
    question: str
    query: str
    api_key: str
    model_id: str
    documents: list[Any]
    relevant: list[Any]
    retries: int
    answer: str
    source: str
    source_label: str
    sources: list[dict]
