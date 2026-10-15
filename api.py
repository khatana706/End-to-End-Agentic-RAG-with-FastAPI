from fastapi import FastAPI
from src.langgraphagenticai.api.routes import router
app = FastAPI(title='End-to-End Agentic Science RAG', version='1.0.0')
app.include_router(router, prefix='/api/v1')
@app.get('/health')
def health(): 
    return {'status':'ok'}
