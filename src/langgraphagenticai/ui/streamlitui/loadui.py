import os, requests, streamlit as st
from src.langgraphagenticai.config import MODELS

def main():
    st.set_page_config(page_title='Science Agentic RAG', page_icon='📘', layout='wide')
    st.title(' End-to-End Agentic Science(class :- 9th) RAG')
    st.caption('PDF-grounded answers with a clearly labelled direct-LLM fallback.')
    with st.sidebar:
        st.header('Settings')
        key=st.text_input('Groq API key', type='password', help='Used for requests; not written to project files or logs.')
        model=st.selectbox('Select Groq model', MODELS)
        base=st.text_input('FastAPI URL', os.getenv('API_BASE_URL','http://127.0.0.1:8000')).rstrip('/')
    question=st.text_area('Ask a question about your PDF', height=100, placeholder='What is the function of the nucleus?')
    if st.button('Get answer', type='primary', disabled=not question.strip()):
        if not key.strip(): 
            st.error('Enter your Groq API key in the sidebar.')
        else:
            try:
                with st.spinner('Running LangGraph workflow...'):
                    r=requests.post(base+'/api/v1/ask',json={'question':question,'api_key':key,'model_id':model},timeout=180)
                if not r.ok: st.error(r.text)
                else: st.session_state['last_answer']=r.json(); st.session_state['api_base']=base
            except requests.RequestException as e: st.error(f'Cannot connect to FastAPI: {e}')
    data=st.session_state.get('last_answer')
    if data:
        st.subheader('Answer')
        (st.warning if data.get('source')=='direct_llm' else st.success)(data.get('source_label',''))
        st.markdown(data.get('answer',''))
        if data.get('sources'):
            st.markdown('**Sources**')
            for s in data['sources']: st.write(f"- {s.get('source_file')}" + (f", page {s['page']}" if s.get('page') else ''))
        st.divider(); st.subheader('Human feedback')
        rating=st.radio('Was this answer useful?', ['Accepted','Rejected'], horizontal=True, key='rating_'+data['answer_id'])
        comment=st.text_area('Optional comment', key='comment_'+data['answer_id'])
        if st.button('Submit feedback', key='feedback_'+data['answer_id']):
            try:
                r=requests.post(st.session_state['api_base']+'/api/v1/feedback',json={'answer_id':data['answer_id'],'rating':rating.lower(),'comment':comment},timeout=20)
                st.success('Feedback saved.') if r.ok else st.error(r.text)
            except requests.RequestException as e: st.error(str(e))
if __name__ == '__main__':
    main()
