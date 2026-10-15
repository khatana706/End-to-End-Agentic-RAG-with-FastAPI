import json
from typing import Literal
from pydantic import BaseModel, Field
from src.langgraphagenticai.LLMS.groqllm import get_llm
from src.langgraphagenticai.vectorstore.store import vectorstore

class Grade(BaseModel):
    binary_score: Literal["yes", "no"] = Field(description="Whether this chunk is relevant to answering the question")

def orchestrator(s):
    response = get_llm(s['api_key'], s['model_id']).invoke(
        "Turn this question into a concise science textbook search query. Return only the query.\nQuestion: " + s['question'])
    return {"query": str(response.content).strip() or s['question']}

# Vector database get documents retrieve 

def retrieve(s):
    return {"documents": vectorstore().similarity_search(s['query'], k=5)}

# Checked the documents of used full or not used full.

def grade_documents(s):
    llm = get_llm(s['api_key'], s['model_id'])
    good = []
    for doc in s.get('documents', []):
        prompt = ('Decide if the document is relevant to answering the question. Return yes or no only as JSON '
                  '{"binary_score":"yes"} or {"binary_score":"no"}. Do not use outside knowledge.\nQuestion: '
                  + s['question'] + '\nDocument: ' + doc.page_content[:4500])
        try:
            grade = llm.with_structured_output(Grade).invoke(prompt).binary_score
        except Exception:
            raw = str(llm.invoke(prompt).content).lower()
            try: 
                grade = json.loads(raw[raw.index('{'):raw.rindex('}')+1]).get('binary_score', 'no')
            except Exception:
                grade = 'yes' if raw.strip() == 'yes' else 'no'
        if grade == 'yes': 
            good.append(doc)
    return {"relevant": good}

# If the documents are not relevant ,than question rewrite again.

def rewrite_question(s):
    response = get_llm(s['api_key'], s['model_id']).invoke(
        "Rewrite as a clearer science textbook retrieval query. Return only the query.\nOriginal question: "
        + s['question'] + "\nPrevious query: " + s.get('query', ''))
    return {"query": str(response.content).strip() or s['question'], "retries": s.get('retries', 0) + 1}

# If the  documents  are releveant than get the answwer from pdf.

def generate_answer(s):
    context, sources = [], []
    for doc in s['relevant']:
        name = doc.metadata.get('source_file', doc.metadata.get('source', 'PDF'))
        page = doc.metadata.get('page')
        label = f"{name}, page {page + 1}" if isinstance(page, int) else name
        context.append(f"[Source: {label}]\n{doc.page_content}")
        sources.append({"source_file": name, "page": page + 1 if isinstance(page, int) else None})
    prompt = ("Answer the original question using ONLY these PDF excerpts. If they do not contain enough evidence, "
              "say so; do not guess. Mention source filename/page where possible.\nQuestion: " + s['question']
              + "\nPDF excerpts:\n" + '\n\n'.join(context))
    answer = str(get_llm(s['api_key'], s['model_id']).invoke(prompt).content)
    return {"answer": answer, "source": "pdf", "source_label": "Answer grounded in relevant PDF content", "sources": sources}

# If the answer not found the pdf than answer from the direct LLM.

def direct_llm(s):
    prompt = ("Answer clearly from general model knowledge. The PDF retrieval system did not find relevant evidence. "
              "Do not claim this answer came from the PDF.\nQuestion: " + s['question'])
    answer = str(get_llm(s['api_key'], s['model_id']).invoke(prompt).content)
    return {"answer": answer, "source": "direct_llm", "source_label": "Direct LLM answer — not grounded in the PDF database", "sources": []}
