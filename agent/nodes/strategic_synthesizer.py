"""
strategic_synthesizer.py — Nodo sintetizador estratégico.
Usa GPT 5.4 Mini (necesita capacidad de razonamiento complejo).
Cruza datos de las 3 fuentes para generar insights de nivel ejecutivo.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import STRATEGIC_SYNTHESIZER_PROMPT
from agent.tools.analytics import format_summary_for_prompt
from agent.state import CafeteriaAgentState

llm_mini = ChatOpenAI(model="gpt-5.4-mini", temperature=0.3)


def synthesize(state: CafeteriaAgentState) -> dict:
    """Cruza insights de los 3 dominios para respuestas estratégicas."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    sales_summary = state.get("sales_summary", {})
    supplier_summary = state.get("supplier_summary", {})
    survey_summary = state.get("survey_summary", {})

    system_prompt = STRATEGIC_SYNTHESIZER_PROMPT.format(
        sales_summary=format_summary_for_prompt(sales_summary),
        supplier_summary=format_summary_for_prompt(supplier_summary),
        survey_summary=format_summary_for_prompt(survey_summary),
    )

    response = llm_mini.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_message),
    ])

    return {
        "analysis_result": response.content,
        "sources_cited": [
            "ventas_cafeteria.csv",
            "reportes_proveedores.json",
            "encuestas_estudiantes.json",
        ],
    }
