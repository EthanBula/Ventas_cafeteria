"""
supplier_analyst.py — Nodo analista de proveedores.
Usa GPT 5.4 Mini.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import SUPPLIER_ANALYST_PROMPT
from agent.tools.analytics import format_summary_for_prompt
from agent.state import CafeteriaAgentState

llm_mini = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)


def analyze(state: CafeteriaAgentState) -> dict:
    """Evaluación de proveedores: cumplimiento, costos, devoluciones, riesgos."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    supplier_summary = state.get("supplier_summary", {})

    system_prompt = SUPPLIER_ANALYST_PROMPT.format(
        supplier_summary=format_summary_for_prompt(supplier_summary)
    )

    response = llm_mini.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_message),
    ])

    return {
        "analysis_result": response.content,
        "sources_cited": ["reportes_proveedores.json"],
    }
