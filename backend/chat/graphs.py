from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, Dict, Any, List
import os


# ============================
# State definition
# ============================
class ChatState(TypedDict):
    document_content: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    current_query: str
    selected_context: str
    answer: str
    is_answerable: bool
    validation_passed: bool


# ============================
# Configuration
# ============================
MAX_CONTEXT_CHARS = 8000


# ============================
# Helpers
# ============================
def is_intellectual_query(query: str) -> bool:
    if not query:
        return False
    q = query.lower()
    return any(k in q for k in [
        "summarize",
        "summary",
        "overview",
        "what is this",
        "what is the pdf about",
        "explain",
        "describe",
        "purpose",
        "objective"
    ])


# ============================
# LLM Utilities (SAFE)
# ============================
def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return None

    try:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    except Exception:
        return None


def call_llm(prompt: str) -> str:
    llm = get_llm()

    if llm is None:
        return (
            "AI is not configured correctly. "
            "Please check your OPENROUTER_API_KEY."
        )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return (
            response.content.strip()
            if hasattr(response, "content")
            else str(response)
        )
    except Exception as e:
        return f"AI error: {str(e)}"


# ============================
# Graph Nodes
# ============================
def context_condenser(state: ChatState) -> ChatState:
    doc = state.get("document_content", {})
    context = ""

    for page_num, page_data in doc.items():
        if isinstance(page_data, dict):
            for sec in page_data.get("sections", []):
                chunk = (
                    f"Page {page_num} - {sec.get('title', 'Section')}\n"
                    f"{sec.get('content', '')}\n\n"
                )
                if len(context) + len(chunk) > MAX_CONTEXT_CHARS:
                    break
                context += chunk
        else:
            chunk = f"Page {page_num}\n{str(page_data)}\n\n"
            if len(context) + len(chunk) > MAX_CONTEXT_CHARS:
                break
            context += chunk

    state["selected_context"] = context
    state["is_answerable"] = bool(context.strip())
    return state


def answer_generator(state: ChatState) -> ChatState:
    query = state.get("current_query", "")
    context = state.get("selected_context", "")

    if not context.strip():
        state["answer"] = (
            "I couldn’t extract readable text from this PDF. "
            "If it is scanned or image-based, OCR may be required."
        )
        return state

    if is_intellectual_query(query):
        prompt = f"""
You are an analytical document assistant.

Using the document below, infer:
- main topic
- purpose
- key ideas

Document:
{context}

Respond clearly and structurally.
"""
    else:
        prompt = f"""
You are a factual document assistant.

Answer ONLY using the document content.
If the answer does not exist, say so.

Document:
{context}

Question:
{query}
"""

    state["answer"] = call_llm(prompt)
    return state


def safety_validator(state: ChatState) -> ChatState:
    state["validation_passed"] = True
    return state


# ============================
# ✅ SAFE GRAPH FACTORY
# ============================
def get_compiled_graph():
    graph = StateGraph(ChatState)

    graph.add_node("context_condenser", context_condenser)
    graph.add_node("answer_generator", answer_generator)
    graph.add_node("safety_validator", safety_validator)

    graph.add_edge(START, "context_condenser")
    graph.add_edge("context_condenser", "answer_generator")
    graph.add_edge("answer_generator", "safety_validator")
    graph.add_edge("safety_validator", END)

    return graph.compile()
