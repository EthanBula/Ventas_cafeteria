"""
router.py — Nodo clasificador de preguntas.
Usa GPT 5.4 Nano (modelo ligero para clasificación rápida).
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import ROUTER_PROMPT
from agent.state import CafeteriaAgentState

# Modelo ligero para clasificación
llm_nano = ChatOpenAI(model="gpt-5.4-nano", temperature=0)

VALID_TYPES = {"ventas", "proveedores", "satisfaccion", "estrategico", "general"}


def classify_query(state: CafeteriaAgentState) -> dict:
    """Clasifica la pregunta del usuario en una de 5 categorías."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    response = llm_nano.invoke([
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=last_message),
    ])

    query_type = response.content.strip().lower().replace('"', "").replace("'", "")

    # Fallback si el modelo retorna algo inesperado
    if query_type not in VALID_TYPES:
        query_type = "general"

    return {"query_type": query_type}
