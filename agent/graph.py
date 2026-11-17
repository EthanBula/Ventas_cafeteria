"""
graph.py — Definición del grafo LangGraph para el agente de cafetería.

Implementa el flujo:
  __start__ → router_node → [analyst/synthesizer/general] → response_formatter → __end__
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente desde la raíz ANTES de importar los nodos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from langgraph.graph import StateGraph, END

from agent.state import CafeteriaAgentState
from agent.nodes import (
    router,
    sales_analyst,
    supplier_analyst,
    survey_analyst,
    strategic_synthesizer,
    general_responder,
    response_formatter,
)
from agent.tools.data_loader import load_all_summaries


def route_query(state: CafeteriaAgentState) -> str:
    """Routing condicional basado en la clasificación del router."""
    return state.get("query_type", "general")


def build_graph():
    """Construye y compila el grafo del agente."""
    builder = StateGraph(CafeteriaAgentState)

    # Agregar nodos
    builder.add_node("router_node", router.classify_query)
    builder.add_node("sales_analyst", sales_analyst.analyze)
    builder.add_node("supplier_analyst", supplier_analyst.analyze)
    builder.add_node("survey_analyst", survey_analyst.analyze)
    builder.add_node("strategic_synthesizer", strategic_synthesizer.synthesize)
    builder.add_node("general_responder", general_responder.respond)
    builder.add_node("response_formatter", response_formatter.format_output)

    # Entry point
    builder.set_entry_point("router_node")

    # Routing condicional
    builder.add_conditional_edges(
        "router_node",
        route_query,
        {
            "ventas": "sales_analyst",
            "proveedores": "supplier_analyst",
            "satisfaccion": "survey_analyst",
            "estrategico": "strategic_synthesizer",
            "general": "general_responder",
        },
    )

    # Todos los analistas convergen en el formateador
    for node in [
        "sales_analyst",
        "supplier_analyst",
        "survey_analyst",
        "strategic_synthesizer",
        "general_responder",
    ]:
        builder.add_edge(node, "response_formatter")

    builder.add_edge("response_formatter", END)

    return builder.compile()


# Pre-cargar resúmenes de datos al importar el módulo
_summaries = load_all_summaries()

# Grafo compilado, listo para usar
graph = build_graph()


def invoke_agent(user_message: str, history: list | None = None) -> str:
    """
    Interfaz simplificada para invocar al agente.
    
    Args:
        user_message: Pregunta del usuario
        history: Historial de mensajes previos (opcional)
    
    Returns:
        Respuesta formateada del agente
    """
    from langchain_core.messages import HumanMessage

    messages = list(history) if history else []
    messages.append(HumanMessage(content=user_message))

    result = graph.invoke({
        "messages": messages,
        "sales_summary": _summaries["sales"],
        "supplier_summary": _summaries["suppliers"],
        "survey_summary": _summaries["surveys"],
    })

    # Extraer el último mensaje AI de la respuesta
    ai_messages = [m for m in result["messages"] if hasattr(m, "type") and m.type == "ai"]
    if ai_messages:
        return ai_messages[-1].content
    return "No se pudo generar una respuesta. Intenta reformular tu pregunta."
