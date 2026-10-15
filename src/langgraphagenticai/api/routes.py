import json, threading, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from src.langgraphagenticai.api.schemas import AskRequest, FeedbackRequest
from src.langgraphagenticai.config import MODELS, ANSWERS_FILE, FEEDBACK_FILE
from src.langgraphagenticai.graph.graph_builder import build_graph
router = APIRouter(); lock = threading.Lock()
def append(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with lock, path.open('a', encoding='utf-8') as f: f.write(json.dumps(data, ensure_ascii=False) + '\n')
def answer_ids():
    ids=set()
    if ANSWERS_FILE.exists():
        for line in ANSWERS_FILE.read_text(encoding='utf-8').splitlines():
            try: ids.add(json.loads(line)['answer_id'])
            except Exception: pass
    return ids
@router.get('/models')
def models(): return {'models': MODELS}
@router.post('/ask')
def ask(req: AskRequest):
    if req.model_id not in MODELS: 
        raise HTTPException(400, 'Choose a configured model')
    try:
        result = build_graph().invoke({'question': req.question.strip(), 'query': req.question.strip(), 'api_key': req.api_key.get_secret_value(), 'model_id': req.model_id, 'retries': 0})
    except FileNotFoundError as e: raise HTTPException(503, str(e))
    except Exception as e: raise HTTPException(502, f'RAG request failed ({type(e).__name__}); check API key/model and server logs')
    aid=str(uuid.uuid4())
    append(ANSWERS_FILE, {'answer_id':aid,'question':req.question.strip(),'source':result.get('source'),'model_id':req.model_id,'created_at':datetime.now(timezone.utc).isoformat()})
    return {'answer_id':aid,'answer':result.get('answer',''),'source':result.get('source','unknown'),'source_label':result.get('source_label',''),'sources':result.get('sources',[])}
@router.post('/feedback')
def feedback(req: FeedbackRequest):
    if req.answer_id not in answer_ids(): raise HTTPException(404, 'Unknown answer_id; submit a question first')
    append(FEEDBACK_FILE, {'answer_id':req.answer_id,'rating':req.rating,'comment':req.comment.strip(),'created_at':datetime.now(timezone.utc).isoformat()})
    return {'status':'feedback_saved','answer_id':req.answer_id}
@router.get('/feedback/stats')
def stats():
    counts={'accepted':0,'rejected':0}
    if FEEDBACK_FILE.exists():
        for line in FEEDBACK_FILE.read_text(encoding='utf-8').splitlines():
            try:
                rating=json.loads(line).get('rating')
                if rating in counts: counts[rating]+=1
            except Exception: pass
    return {**counts,'total':sum(counts.values())}
