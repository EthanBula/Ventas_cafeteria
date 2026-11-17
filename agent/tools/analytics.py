"""
analytics.py — Funciones de análisis reutilizables para los nodos del agente.
"""

import json


def format_summary_for_prompt(summary: dict) -> str:
    """Serializa un resumen a JSON legible para inyectar en prompts."""
    return json.dumps(summary, ensure_ascii=False, indent=2)


def get_top_n(data: dict, n: int = 5, ascending: bool = False) -> dict:
    """Retorna los top N items de un diccionario numérico."""
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=not ascending)
    return dict(sorted_items[:n])
