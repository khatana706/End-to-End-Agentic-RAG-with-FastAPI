from langgraph.graph import StateGraph, START, END
from src.langgraphagenticai.state.state import RAGState

from src.langgraphagenticai.config import MAX_REWRITES
from src.langgraphagenticai.nodes.nodes import orchestrator, retrieve, grade_documents, rewrite_question, generate_answer, direct_llm

def route(s):
    # answer is relevant than answer get from database

    if s.get('relevant'): 
        return 'generate_answer'

    # question rewrite 
    if s.get('retries', 0) < MAX_REWRITES: 
        return 'rewrite_question'
    
    # Otherwise answer direct llm
    return 'direct_llm'

def build_graph():
    g = StateGraph(RAGState)

    nodes_list = [
        ('orchestrator', orchestrator),
        ('retrieve', retrieve), 
        ('grade_documents', grade_documents), 
        ('rewrite_question', rewrite_question),
        ('generate_answer', generate_answer), 
        ('direct_llm', direct_llm)
    ]

    for name, fn in nodes_list:
        # Yahan name aur function ka naam print kar rahe hain
        # print(f"Adding Node -> Name: {name} | Function: {fn.__name__}")
        g.add_node(name, fn)
    
    g.add_edge(START, 'orchestrator')
    g.add_edge('orchestrator', 'retrieve')
    g.add_edge('retrieve', 'grade_documents')

    g.add_conditional_edges(
        'grade_documents', 
        route, 
        {
            'generate_answer': 'generate_answer',
            'rewrite_question': 'rewrite_question',
            'direct_llm': 'direct_llm'
        }
    )

    g.add_edge('rewrite_question', 'retrieve')
    g.add_edge('generate_answer', END)
    g.add_edge('direct_llm', END)
    
    compiled_graph = g.compile()
    
    # --- Mermaid PNG Image Saved
    print("\n--- Generating Workflow Image ---")
    try:
        image_bytes = compiled_graph.get_graph().draw_mermaid_png()
        file_path = "rag_workflow.png"
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Workflow diagram successfully saved as '{file_path}'!")
    except Exception as e:
        print(f"Could not save image automatically: {e}")
    
    return compiled_graph


if __name__ == "__main__":

    app = build_graph()
    print("\n Graph built and compiled successfully!")
