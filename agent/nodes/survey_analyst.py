"""
survey_analyst.py — Nodo analista de encuestas / satisfacción.
Usa GPT 5.4 Mini.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import SURVEY_ANALYST_PROMPT
from agent.tools.analytics import format_summary_for_prompt
from agent.state import CafeteriaAgentState

llm_mini = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)


def analyze(state: CafeteriaAgentState) -> dict:
    """Análisis de satisfacción: NPS, sentimiento, correlaciones demográficas."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    survey_summary = state.get("survey_summary", {})

    system_prompt = SURVEY_ANALYST_PROMPT.format(
        survey_summary=format_summary_for_prompt(survey_summary)
    )

    response = llm_mini.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_message),
    ])

    return {
        "analysis_result": response.content,
        "sources_cited": ["encuestas_estudiantes.json"],
    }
