"""
state.py — Definición del estado del grafo LangGraph.
"""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class CafeteriaAgentState(TypedDict):
    """Estado compartido entre todos los nodos del grafo."""

    # Historial conversacional
    messages: Annotated[list, add_messages]

    # Clasificación de la consulta
    query_type: Literal[
        "ventas", "proveedores", "satisfaccion",
        "estrategico", "general",
    ]

    # Datos cargados (se inyectan al inicio)
    sales_summary: dict
    supplier_summary: dict
    survey_summary: dict

    # Resultado del análisis del nodo especialista
    analysis_result: str

    # Fuentes citadas en la respuesta
    sources_cited: list[str]
