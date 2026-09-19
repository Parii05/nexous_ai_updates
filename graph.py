from langgraph.graph import StateGraph, END
from rag import RAGState, router_node, retrieve_documents_node, retrieve_memory_node, generate_answer_node, direct_answer_node, extract_store_memory_node


def build_rag_graph():
    """Create a simple LangGraph workflow from the existing RAG steps."""

    workflow = StateGraph(RAGState)
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve_documents", retrieve_documents_node)
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("direct_answer", direct_answer_node)
    workflow.add_node("extract_store_memory", extract_store_memory_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        lambda state: "direct_answer" if not state.get("needs_retrieval") else "retrieve_documents",
        {
            "direct_answer": "direct_answer",
            "retrieve_documents": "retrieve_documents",
        },
    )

    workflow.add_edge("retrieve_documents", "retrieve_memory")
    workflow.add_edge("retrieve_memory", "generate_answer")
    workflow.add_edge("generate_answer", "extract_store_memory")
    workflow.add_edge("direct_answer", "extract_store_memory")
    workflow.add_edge("extract_store_memory", END)

    return workflow.compile()
