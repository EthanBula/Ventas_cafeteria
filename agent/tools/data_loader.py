"""
data_loader.py — Carga y pre-procesamiento de las 3 fuentes de datos.

Pre-computa resúmenes estadísticos para inyectar en los prompts del LLM,
evitando enviar datos crudos y reduciendo tokens consumidos por invocación.
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Ruta base del proyecto (dos niveles arriba de este archivo)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _calcular_declive(df: pd.DataFrame) -> float:
    """Calcula el porcentaje de declive en transacciones mensuales (Ene vs Dic)."""
    monthly = df.groupby("Mes").size()
    if 1 in monthly.index and 12 in monthly.index:
        return round((monthly[12] - monthly[1]) / monthly[1] * 100, 2)
    return 0.0


def build_sales_summary(csv_path: str | None = None) -> dict:
    """
    Genera un resumen pre-computado del CSV de ventas.
    Retorna un diccionario inyectable en los prompts del agente.
    """
    if csv_path is None:
        csv_path = str(BASE_DIR / "ventas_cafeteria.csv")

    df = pd.read_csv(csv_path)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.month
    df["Hora_int"] = df["Hora"].str[:2].astype(int)
    df["DiaSemana"] = df["Fecha"].dt.day_name()

    ventas_por_mes = df.groupby("Mes")["Valor Total"].sum().round(2)
    transacciones_por_mes = df.groupby("Mes").size()

    return {
        "total_transacciones": int(len(df)),
        "ingreso_total_usd": round(float(df["Valor Total"].sum()), 2),
        "ticket_promedio_usd": round(float(df["Valor Total"].mean()), 2),
        "ventas_por_mes": {int(k): float(v) for k, v in ventas_por_mes.items()},
        "transacciones_por_mes": {int(k): int(v) for k, v in transacciones_por_mes.items()},
        "top_5_productos_ingreso": {
            k: round(float(v), 2)
            for k, v in df.groupby("Nombre de Producto")["Valor Total"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .items()
        },
        "bottom_5_productos_ingreso": {
            k: round(float(v), 2)
            for k, v in df.groupby("Nombre de Producto")["Valor Total"]
            .sum()
            .sort_values(ascending=True)
            .head(5)
            .items()
        },
        "distribucion_horaria": {
            int(k): int(v)
            for k, v in df.groupby("Hora_int").size().items()
        },
        "ventas_por_dia_semana": {
            k: round(float(v), 2)
            for k, v in df.groupby("DiaSemana")["Valor Total"].sum().items()
        },
        "tendencia_declive_pct": _calcular_declive(df),
        "productos_unicos": sorted(df["Nombre de Producto"].unique().tolist()),
        "periodo": f"{df['Fecha'].min().date()} a {df['Fecha'].max().date()}",
    }


def build_supplier_summary(json_path: str | None = None) -> dict:
    """
    Genera un resumen de los reportes de proveedores.
    """
    if json_path is None:
        json_path = str(BASE_DIR / "reportes_proveedores.json")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    reportes = data["reportes"]

    # Resumen por proveedor
    proveedores = {}
    for r in reportes:
        nombre = r["proveedor"]["nombre"]
        if nombre not in proveedores:
            proveedores[nombre] = {
                "categoria": r["proveedor"]["categoria"],
                "productos_asociados": r["productos_cafeteria_asociados"],
                "meses": [],
                "calificaciones": [],
                "tasas_cumplimiento": [],
                "costos_totales": [],
                "unidades_devueltas": [],
                "unidades_solicitadas": [],
                "factores_demanda": [],
            }
        p = proveedores[nombre]
        p["meses"].append(r["mes"])
        p["calificaciones"].append(r["calificacion_servicio_proveedor"])
        p["tasas_cumplimiento"].append(r["entregas"]["tasa_cumplimiento"])
        p["costos_totales"].append(r["volumen_pedido"]["costo_total_usd"])
        p["unidades_devueltas"].append(r["volumen_pedido"]["unidades_devueltas"])
        p["unidades_solicitadas"].append(r["volumen_pedido"]["unidades_solicitadas"])
        p["factores_demanda"].append(r["factor_demanda_relativo"])

    resumen_proveedores = {}
    for nombre, p in proveedores.items():
        resumen_proveedores[nombre] = {
            "categoria": p["categoria"],
            "productos_asociados": p["productos_asociados"],
            "calificacion_promedio": round(float(np.mean(p["calificaciones"])), 2),
            "tasa_cumplimiento_promedio": round(float(np.mean(p["tasas_cumplimiento"])), 1),
            "costo_total_anual_usd": round(float(np.sum(p["costos_totales"])), 2),
            "total_unidades_solicitadas": int(np.sum(p["unidades_solicitadas"])),
            "total_unidades_devueltas": int(np.sum(p["unidades_devueltas"])),
            "tasa_devolucion_pct": round(
                float(np.sum(p["unidades_devueltas"]) / np.sum(p["unidades_solicitadas"]) * 100), 2
            ),
            "factor_demanda_enero": p["factores_demanda"][0],
            "factor_demanda_diciembre": p["factores_demanda"][-1],
        }

    return {
        "total_reportes": len(reportes),
        "total_proveedores": len(proveedores),
        "periodo": data["metadata"]["periodo"],
        "proveedores": resumen_proveedores,
    }


def build_survey_summary(json_path: str | None = None) -> dict:
    """
    Genera un resumen de las encuestas de satisfacción estudiantil.
    """
    if json_path is None:
        json_path = str(BASE_DIR / "encuestas_estudiantes.json")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    encuestas = data["encuestas"]
    total = len(encuestas)

    # Calificaciones promedio globales
    cal_keys = [
        "calidad_alimentos", "variedad_menu", "atencion_servicio",
        "relacion_precio_calidad", "limpieza_ambiente", "satisfaccion_general",
    ]
    cal_sums = {k: 0.0 for k in cal_keys}
    for e in encuestas:
        for k in cal_keys:
            cal_sums[k] += e["calificaciones"][k]
    cal_promedios = {k: round(v / total, 2) for k, v in cal_sums.items()}

    # Frecuencia de visita
    freq_counts = {}
    for e in encuestas:
        fv = e["frecuencia_visita"]
        freq_counts[fv] = freq_counts.get(fv, 0) + 1

    # Tasa de recomendación (proxy NPS)
    recomienda = sum(1 for e in encuestas if e["recomienda_cafeteria"])
    tasa_recomendacion = round(recomienda / total * 100, 1)

    # Producto más consumido (distribución)
    prod_counts = {}
    for e in encuestas:
        p = e["producto_mas_consumido"]
        prod_counts[p] = prod_counts.get(p, 0) + 1
    top_productos = dict(sorted(prod_counts.items(), key=lambda x: -x[1])[:5])

    # Distribución por carrera
    carrera_counts = {}
    for e in encuestas:
        c = e["estudiante"]["carrera"]
        carrera_counts[c] = carrera_counts.get(c, 0) + 1

    # Gasto semanal promedio
    gastos = [e["gasto_semanal_estimado_usd"] for e in encuestas]

    # Calificaciones por mes (para ver tendencia de deterioro)
    from datetime import datetime
    cal_por_mes = {}
    for e in encuestas:
        mes = datetime.strptime(e["fecha"], "%Y-%m-%d").month
        if mes not in cal_por_mes:
            cal_por_mes[mes] = []
        cal_por_mes[mes].append(e["calificaciones"]["satisfaccion_general"])
    satisfaccion_por_mes = {
        int(m): round(float(np.mean(vals)), 2)
        for m, vals in sorted(cal_por_mes.items())
    }

    # Comentarios muestra (primeros 10 negativos para contexto)
    comentarios_negativos = []
    for e in encuestas:
        if not e["recomienda_cafeteria"] and len(comentarios_negativos) < 10:
            comentarios_negativos.append(e["comentario"])

    return {
        "total_encuestas": total,
        "periodo": data["metadata"]["periodo"],
        "calificaciones_promedio": cal_promedios,
        "frecuencia_visita_distribucion": freq_counts,
        "tasa_recomendacion_pct": tasa_recomendacion,
        "top_5_productos_consumidos": top_productos,
        "distribucion_carreras": dict(sorted(carrera_counts.items(), key=lambda x: -x[1])),
        "gasto_semanal_promedio_usd": round(float(np.mean(gastos)), 2),
        "gasto_semanal_mediana_usd": round(float(np.median(gastos)), 2),
        "satisfaccion_general_por_mes": satisfaccion_por_mes,
        "muestra_comentarios_negativos": comentarios_negativos,
    }


def load_all_summaries() -> dict:
    """Carga los 3 resúmenes de datos. Se invoca al iniciar el agente."""
    return {
        "sales": build_sales_summary(),
        "suppliers": build_supplier_summary(),
        "surveys": build_survey_summary(),
    }
