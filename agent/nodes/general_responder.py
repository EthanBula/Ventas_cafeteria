"""
general_responder.py — Nodo para preguntas generales / fuera de alcance.
Usa GPT 5.4 Nano (modelo ligero para respuestas simples).
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.prompts.system_prompts import GENERAL_RESPONDER_PROMPT
from agent.state import CafeteriaAgentState

llm_nano = ChatOpenAI(model="gpt-5.4-nano", temperature=0.5)


def respond(state: CafeteriaAgentState) -> dict:
    """Maneja preguntas generales, saludos y consultas fuera de alcance."""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    response = llm_nano.invoke([
        SystemMessage(content=GENERAL_RESPONDER_PROMPT),
        HumanMessage(content=last_message),
    ])

    return {
        "analysis_result": response.content,
        "sources_cited": [],
    }
