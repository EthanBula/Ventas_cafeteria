"""
response_formatter.py — Nodo formateador de respuestas finales.
Usa GPT 5.4 Nano para formateo ligero.
Agrega fuentes citadas y produce la respuesta final para el usuario.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agent.prompts.system_prompts import RESPONSE_FORMATTER_PROMPT
from agent.state import CafeteriaAgentState

llm_nano = ChatOpenAI(model="gpt-5.4-nano", temperature=0.1)


def format_output(state: CafeteriaAgentState) -> dict:
    """Formatea la respuesta final con fuentes citadas."""
    analysis = state.get("analysis_result", "")
    sources = state.get("sources_cited", [])

    # Si el análisis ya está bien formateado, lo usamos directamente
    # agregando las fuentes al final
    if sources:
        sources_text = "\n\n---\n📂 **Fuentes**: " + ", ".join(f"`{s}`" for s in sources)
    else:
        sources_text = ""

    # Usar el modelo para pulir el formato
    format_prompt = f"""Formatea la siguiente respuesta de análisis para presentarla al usuario.
Mantén todo el contenido cuantitativo intacto. Asegúrate de usar markdown claro.

ANÁLISIS:
{analysis}

FUENTES A INCLUIR AL FINAL:
{', '.join(sources) if sources else 'Ninguna'}"""

    response = llm_nano.invoke([
        SystemMessage(content=RESPONSE_FORMATTER_PROMPT),
        HumanMessage(content=format_prompt),
    ])

    formatted_response = response.content + sources_text

    return {
        "messages": [AIMessage(content=formatted_response)],
    }
