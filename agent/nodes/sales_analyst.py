"""
sales_analyst.py — Nodo analista de ventas.
Usa GPT 5.4 Mini (modelo más potente para análisis complejos).
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import SALES_ANALYST_PROMPT
from agent.tools.analytics import format_summary_for_prompt
from agent.state import CafeteriaAgentState

llm_mini = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)


def analyze(state: CafeteriaAgentState) -> dict:
    """Análisis cuantitativo de ventas: tendencias, estacionalidad, productos, horas pico."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    sales_summary = state.get("sales_summary", {})

    system_prompt = SALES_ANALYST_PROMPT.format(
        sales_summary=format_summary_for_prompt(sales_summary)
    )

    response = llm_mini.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_message),
    ])

    return {
        "analysis_result": response.content,
        "sources_cited": ["ventas_cafeteria.csv"],
    }
