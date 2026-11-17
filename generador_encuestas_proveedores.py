"""
Generador de datos sintéticos complementarios para la cafetería universitaria.
Produce:
  1. encuestas_estudiantes.json  – Encuestas de satisfacción de estudiantes
  2. reportes_proveedores.json   – Reportes mensuales de proveedores

Coherente con generador_ventas.py:
  • Mismo menú y precios
  • Mismo periodo: 2025-01-01 → 2025-12-31
  • Declive lineal ~20 % reflejado en sentimiento y volúmenes de pedido
"""

import json
import random
import uuid
from datetime import datetime, timedelta

# ────────────────────────────────────────────────────────────────────
# Datos compartidos con generador_ventas.py
# ────────────────────────────────────────────────────────────────────
menu = {
    "Café Americano": 1.50, "Café Latte": 2.50, "Capuccino": 2.50,
    "Té Helado": 2.00, "Agua Embotellada": 1.00, "Refresco": 1.50,
    "Sandwich de Pollo": 4.50, "Sandwich Vegetariano": 4.00,
    "Croissant": 2.00, "Galleta con Chispas": 1.20,
    "Muffin de Arándanos": 2.20, "Ensalada César": 5.00, "Empanada de Carne": 2.00
}
products = list(menu.keys())

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
days_in_year = (end_date - start_date).days + 1

DECLINE_START = 1.0
DECLINE_END   = 0.8

# ────────────────────────────────────────────────────────────────────
# Catálogos auxiliares
# ────────────────────────────────────────────────────────────────────
carreras = [
    "Ingeniería de Sistemas", "Administración de Empresas", "Derecho",
    "Medicina", "Psicología", "Comunicación Social", "Arquitectura",
    "Contaduría Pública", "Ingeniería Industrial", "Biología",
    "Economía", "Diseño Gráfico", "Enfermería", "Matemáticas"
]

nombres_m = [
    "Andrés", "Carlos", "David", "Felipe", "Gabriel", "Hugo",
    "Iván", "Jorge", "Luis", "Manuel", "Nicolás", "Óscar",
    "Pablo", "Ricardo", "Santiago", "Tomás", "Valentín", "Daniel"
]
nombres_f = [
    "Ana", "Beatriz", "Camila", "Diana", "Elena", "Fernanda",
    "Gabriela", "Helena", "Isabel", "Julia", "Karen", "Laura",
    "María", "Natalia", "Olga", "Patricia", "Rosa", "Sara", "Valentina"
]
apellidos = [
    "García", "Rodríguez", "Martínez", "López", "González",
    "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres",
    "Flores", "Rivera", "Gómez", "Díaz", "Reyes",
    "Morales", "Ortiz", "Silva", "Vargas", "Castro"
]

# Proveedores con los insumos que suministran a la cafetería
proveedores = [
    {
        "nombre": "Distribuidora Café Premium S.A.S.",
        "nit": "900.123.456-7",
        "contacto": "ventas@cafepremium.co",
        "insumos": ["Café tostado molido (arabica)", "Café tostado molido (blend)", "Leche para espumar"],
        "productos_cafeteria": ["Café Americano", "Café Latte", "Capuccino"],
        "categoria": "Bebidas calientes"
    },
    {
        "nombre": "Bebidas y Refrescos del Valle Ltda.",
        "nit": "800.654.321-0",
        "contacto": "pedidos@bebidasvalle.com",
        "insumos": ["Té negro en hojas", "Jarabe de frutas", "Agua purificada 20L", "Refrescos embotellados 350ml"],
        "productos_cafeteria": ["Té Helado", "Agua Embotellada", "Refresco"],
        "categoria": "Bebidas frías"
    },
    {
        "nombre": "Panadería Industrial El Trigal S.A.",
        "nit": "901.987.654-3",
        "contacto": "comercial@eltrigal.co",
        "insumos": ["Pan para sandwich", "Croissants pre-horneados", "Masa de empanada", "Mezcla para muffins", "Masa para galletas"],
        "productos_cafeteria": ["Sandwich de Pollo", "Sandwich Vegetariano", "Croissant", "Empanada de Carne", "Muffin de Arándanos", "Galleta con Chispas"],
        "categoria": "Panadería y repostería"
    },
    {
        "nombre": "Frescos & Proteínas Corp.",
        "nit": "860.111.222-5",
        "contacto": "logistica@frescosyproteinas.co",
        "insumos": ["Pechuga de pollo", "Lechuga romana", "Queso parmesano", "Carne molida", "Vegetales surtidos", "Arándanos deshidratados"],
        "productos_cafeteria": ["Sandwich de Pollo", "Ensalada César", "Empanada de Carne", "Sandwich Vegetariano", "Muffin de Arándanos"],
        "categoria": "Proteínas y frescos"
    },
    {
        "nombre": "Lácteos y Derivados San Miguel",
        "nit": "830.555.777-9",
        "contacto": "ventas@lacteossanmiguel.com",
        "insumos": ["Leche entera 10L", "Crema de leche", "Mantequilla", "Chispas de chocolate"],
        "productos_cafeteria": ["Café Latte", "Capuccino", "Galleta con Chispas", "Croissant"],
        "categoria": "Lácteos e insumos"
    }
]

# ────────────────────────────────────────────────────────────────────
# Plantillas de comentarios para encuestas (varían con el sentimiento)
# ────────────────────────────────────────────────────────────────────

# Comentarios positivos (→ recomienda = True)
comentarios_positivos = [
    # --- Sobre productos específicos ---
    "Me gusta el {producto}, siempre está fresco y a buen precio.",
    "El {producto} es mi favorito, lo compro casi todos los días.",
    "Los precios son accesibles para estudiantes, especialmente el {producto}.",
    "Me encanta que hayan incorporado opciones como el {producto}.",
    "El personal es muy amable y el {producto} siempre está bien preparado.",
    "El {producto} me salva las mañanas antes del parcial.",
    "Siempre pido {producto} después de clase de las 10, nunca me decepciona.",
    "El {producto} tiene una relación calidad-precio excelente.",
    "Desde que probé el {producto} no he dejado de comprarlo.",
    "El {producto} de aquí es mejor que el de la cafetería del edificio B.",
    # --- Sobre el ambiente y servicio ---
    "La cafetería tiene buen ambiente para estudiar entre clases.",
    "Buen servicio, las filas no son tan largas como antes.",
    "Ambiente agradable y buena variedad en el menú.",
    "Muy buen lugar para almorzar rápido entre clases.",
    "Me gusta que sea un espacio tranquilo para repasar antes de los exámenes.",
    "El trato del personal siempre es cordial, eso se valora.",
    "Me siento cómodo estudiando ahí con mis compañeros de grupo.",
    "Es el punto de encuentro de nuestro grupo de estudio, funciona perfecto.",
    "Se nota que cuidan la presentación de los productos, todo se ve apetitoso.",
    "La cafetería tiene buena iluminación y las mesas están siempre limpias.",
    # --- Sobre conveniencia y precio ---
    "Es la opción más práctica entre bloques de clase.",
    "Me queda perfecto entre la clase de las 9 y la de las 11.",
    "Los combos de desayuno son muy convenientes para el bolsillo estudiantil.",
    "Comparado con comer afuera del campus, aquí sale mucho más barato.",
    "Me ahorro tiempo y dinero comiendo aquí en vez de salir del campus.",
    "El horario es muy conveniente, puedo pasar a cualquier hora del día.",
    "La atención es rápida, en 5 minutos ya tengo mi pedido listo.",
    "Recomiendo totalmente la cafetería, sobre todo para quienes tienen poco tiempo.",
    "Excelente opción para desayunar antes de la primera clase.",
    "Es de los pocos lugares en campus donde puedes sentarte a comer tranquilo.",
]

# Comentarios neutros (→ recomienda basado en satisfacción general)
comentarios_neutros = [
    # --- Observaciones mixtas ---
    "El {producto} está bien, pero podría ser un poco más grande la porción.",
    "Está bien para comer algo rápido, aunque nada extraordinario.",
    "A veces el {producto} está muy bueno y otras veces no tanto, falta consistencia.",
    "El espacio es limitado en horas pico, pero la comida está correcta.",
    "El {producto} cumple, aunque preferiría más variedad en el menú.",
    "Los precios son normales para una cafetería universitaria, ni caros ni baratos.",
    "El {producto} no es el mejor que he probado, pero es aceptable por el precio.",
    "Algunos días la atención es buena y otros no tanto, depende de quién atienda.",
    "La calidad es aceptable, aunque hay margen de mejora en la frescura.",
    "Ni bien ni mal, simplemente cumple con lo básico.",
    # --- Sugerencias constructivas ---
    "El menú debería tener más opciones saludables además de {producto}.",
    "Me gustaría que hubiera WiFi más estable en la zona de la cafetería.",
    "Debería haber más mesas disponibles durante la hora del almuerzo.",
    "Ojalá abrieran más temprano, a las 7 ya hay gente esperando.",
    "Estaría bien que incluyeran opciones veganas en el menú.",
    "Sería bueno que pusieran un buzón de sugerencias visible.",
    "Me gustaría que tuvieran promociones o descuentos para estudiantes frecuentes.",
    "Podrían mejorar la señalización del menú, a veces no sé qué hay disponible.",
    "Sería ideal que tuvieran un sistema de pedidos por app para no hacer fila.",
    "La música de fondo está bien, pero a veces el volumen es muy alto.",
    # --- Comparaciones y contexto ---
    "He comido en peores cafeterías universitarias, esta no está mal.",
    "Comparado con el semestre pasado, la calidad se mantiene más o menos igual.",
    "Mis amigos prefieren traer comida de casa, pero yo sigo viniendo de vez en cuando.",
    "Para lo que es una cafetería de campus, está dentro del promedio.",
    "Hay días que vale la pena y días que no, depende de lo que haya disponible.",
    "El {producto} es pasable, pero me gustaría que innovaran un poco más.",
    "No me quejo mucho, pero tampoco es algo que recomiende con entusiasmo.",
    "La ubicación es conveniente, eso es lo que más me hace venir.",
    "A veces el {producto} tarda mucho en salir, pero cuando llega está bien.",
    "El lugar tiene potencial, pero le falta un poco más de cuidado en los detalles.",
]

# Comentarios negativos (→ recomienda = False)
comentarios_negativos = [
    # --- Sobre calidad de productos ---
    "Últimamente el {producto} no sabe como antes, creo que bajaron la calidad de los insumos.",
    "El {producto} estaba frío cuando lo compré, muy decepcionante.",
    "Cada vez hay menos gente comprando aquí, y se nota en la frescura del {producto}.",
    "Me encontré un {producto} que no estaba fresco, eso no debería pasar.",
    "Compré {producto} y no tenía buen sabor, no creo que vuelva pronto.",
    "El {producto} de hoy parecía del día anterior, la textura era rara.",
    "Le pedí {producto} y estaba demasiado seco, como si llevara horas en el mostrador.",
    "La porción de {producto} era ridículamente pequeña para lo que cobran.",
    "El {producto} me cayó mal al estómago, no sé qué le habrán puesto.",
    "Noté que el {producto} ya no tiene el mismo sabor de principio de año.",
    # --- Sobre precios y valor ---
    "Los precios han subido y las porciones son más pequeñas, no vale la pena.",
    "Prefiero ir a comer afuera del campus, la cafetería ya no vale lo que cobra.",
    "La competencia afuera del campus tiene mejor calidad y precios similares.",
    "Por lo que cuesta el {producto} aquí, afuera consigo algo mucho mejor.",
    "El {producto} está caro para lo que ofrecen, antes al menos era más grande.",
    "Con lo que gasto aquí en una semana, como mejor en los restaurantes de la cuadra.",
    "No entiendo por qué subieron los precios si la calidad bajó.",
    "Mis compañeros y yo preferimos pedir delivery, nos sale casi igual y es mejor.",
    "Antes el {producto} era una buena opción económica, ahora ya no tanto.",
    "La relación calidad-precio ha empeorado notablemente este semestre.",
    # --- Sobre servicio y ambiente ---
    "La atención ha empeorado mucho, los empleados parecen desmotivados.",
    "Las filas son cortas ahora, pero es porque ya nadie viene, no porque sean eficientes.",
    "Me da pereza ir a la cafetería, siempre es lo mismo de siempre.",
    "Falta limpieza en las mesas y en los baños cercanos, da mala impresión.",
    "El aire acondicionado nunca funciona bien, es incómodo comer ahí con calor.",
    "Llevo semanas sin encontrar {producto} disponible, siempre se agota temprano.",
    "El menú no cambia nunca, llevamos meses con las mismas opciones.",
    "El personal ni saluda cuando uno llega, se siente uno como un estorbo.",
    "Las mesas siempre están sucias a la hora del almuerzo, nadie las limpia.",
    "El lugar se ve descuidado, las sillas están rotas y nadie las arregla.",
    # --- Sobre la experiencia general ---
    "Honestamente, no recomendaría la cafetería a un compañero nuevo.",
    "He dejado de venir seguido porque la experiencia ya no es agradable.",
    "Antes era mi lugar favorito en el campus, ahora prefiero buscar alternativas.",
    "La cafetería ha perdido mucho encanto desde que empezó el año.",
    "Cada vez conozco más compañeros que dejaron de venir por las mismas razones.",
    "Si no mejoran pronto, van a perder a los pocos clientes que les quedan.",
    "Me resulta más cómodo llevar almuerzo de casa que pasar por aquí.",
    "La última vez que vine me arrepentí, no vuelvo hasta que mejoren.",
    "Es triste ver cómo ha decaído este lugar comparado con el año pasado.",
    "No le veo futuro a la cafetería si siguen así, ya casi no hay clientes.",
]

# Razones para reducir frecuencia (encuestas del segundo semestre)
razones_menor_frecuencia = [
    "Prefiero traer almuerzo de casa, me sale más barato.",
    "Hay más opciones de comida cerca del campus ahora.",
    "Los precios me parecen altos para el tamaño de las porciones.",
    "La calidad ha bajado mucho en los últimos meses.",
    "No encuentro opciones saludables que me gusten.",
    "Mis horarios cambiaron y ya no paso por la cafetería.",
    "La app de delivery me sale más cómodo y con mejor variedad.",
    "Prefiero la cafetería nueva que abrieron en el otro edificio.",
    "Ya no me gusta el sabor, cambiaron algo en la preparación.",
    "Me aburrí del menú, siempre es exactamente igual.",
    "Mis amigos dejaron de ir y ya no tiene gracia ir solo.",
    "Encontré un puesto de comida en la entrada del campus que es mucho mejor.",
    "La higiene del lugar me genera desconfianza últimamente.",
    "Tuve una mala experiencia y no me han dado ganas de volver.",
    "El ambiente ya no es agradable, se siente abandonado.",
]

# Sentimiento asociado a cada pool (para derivar recomienda)
_SENTIMIENTO_POSITIVO = "positivo"
_SENTIMIENTO_NEUTRO   = "neutro"
_SENTIMIENTO_NEGATIVO = "negativo"


def _decline_factor(day_index: int) -> float:
    """Mismo factor de declive que generador_ventas.py"""
    return DECLINE_START + (DECLINE_END - DECLINE_START) * (day_index / (days_in_year - 1))


def _random_date_in_range(month_start: int, month_end: int) -> str:
    """Fecha aleatoria dentro de un rango de meses (1-indexed)."""
    d0 = datetime(2025, month_start, 1)
    if month_end == 12:
        d1 = datetime(2025, 12, 31)
    else:
        d1 = datetime(2025, month_end + 1, 1) - timedelta(days=1)
    delta = (d1 - d0).days
    return (d0 + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


# ================================================================
# 1. GENERADOR DE ENCUESTAS DE ESTUDIANTES
# ================================================================
def generar_encuestas(n: int = 2400) -> list[dict]:
    """
    Genera n encuestas de satisfacción distribuidas a lo largo de 2025.
    Las encuestas del primer trimestre tienden a ser más positivas;
    las del tercer/cuarto trimestre reflejan el deterioro coherente
    con la caída del 20 % en ventas.
    """
    encuestas = []

    # Pools con su sentimiento asociado
    pools_con_sentimiento = [
        (comentarios_positivos, _SENTIMIENTO_POSITIVO),
        (comentarios_neutros,   _SENTIMIENTO_NEUTRO),
        (comentarios_negativos, _SENTIMIENTO_NEGATIVO),
    ]

    for i in range(n):
        # Distribuir las encuestas a lo largo del año con más peso en 2do semestre
        # (refleja que la institución aplica más encuestas al notar la caída)
        month_weights = [6, 6, 8, 8, 10, 10, 14, 14, 16, 16, 18, 18]
        mes = random.choices(range(1, 13), weights=month_weights, k=1)[0]
        fecha = _random_date_in_range(mes, mes)
        day_index = (datetime.strptime(fecha, "%Y-%m-%d") - start_date).days
        factor = _decline_factor(day_index)

        # Datos del estudiante
        genero = random.choice(["M", "F"])
        if genero == "M":
            nombre = random.choice(nombres_m)
        else:
            nombre = random.choice(nombres_f)
        apellido = random.choice(apellidos)
        semestre = random.randint(1, 10)
        carrera = random.choice(carreras)

        # Producto más consumido (el que mencionan en la encuesta)
        producto_favorito = random.choice(products)

        # Calificaciones: se degradan linealmente con el factor de declive
        # factor=1.0 → más probable puntuación alta; factor=0.8 → más baja
        def _rating(base_high_prob: float) -> int:
            # base_high_prob = probabilidad de dar 4-5 cuando factor=1.0
            adjusted = base_high_prob * factor
            r = random.random()
            if r < adjusted * 0.4:
                return 5
            elif r < adjusted * 0.85:
                return 4
            elif r < adjusted * 0.85 + (1 - adjusted) * 0.4:
                return 3
            elif r < adjusted * 0.85 + (1 - adjusted) * 0.8:
                return 2
            else:
                return 1

        calidad_alimentos = _rating(0.80)
        variedad_menu = _rating(0.65)
        atencion_servicio = _rating(0.75)
        relacion_precio_calidad = _rating(0.70)
        limpieza_ambiente = _rating(0.72)
        satisfaccion_general = round(
            (calidad_alimentos + variedad_menu + atencion_servicio
             + relacion_precio_calidad + limpieza_ambiente) / 5, 1
        )

        # Frecuencia de visita (se reduce con el factor)
        if factor > 0.92:
            freq_weights = [0.35, 0.35, 0.20, 0.10]
        elif factor > 0.85:
            freq_weights = [0.20, 0.30, 0.30, 0.20]
        else:
            freq_weights = [0.10, 0.20, 0.30, 0.40]
        frecuencia = random.choices(
            ["Diariamente", "3-4 veces por semana", "1-2 veces por semana", "Ocasionalmente"],
            weights=freq_weights, k=1
        )[0]

        # Seleccionar pool de comentarios según factor de declive
        if factor > 0.92:
            sent_weights = [0.55, 0.30, 0.15]
        elif factor > 0.85:
            sent_weights = [0.25, 0.35, 0.40]
        else:
            sent_weights = [0.10, 0.20, 0.70]

        pool, sentimiento = random.choices(pools_con_sentimiento, weights=sent_weights, k=1)[0]
        comentario = random.choice(pool).format(producto=producto_favorito)

        # ¿Recomendaría la cafetería? — COHERENTE con el sentimiento del comentario
        if sentimiento == _SENTIMIENTO_POSITIVO:
            # Comentario positivo → recomienda (con pequeña probabilidad de no)
            recomienda = random.random() < 0.92
        elif sentimiento == _SENTIMIENTO_NEGATIVO:
            # Comentario negativo → no recomienda (con pequeña probabilidad de sí)
            recomienda = random.random() < 0.08
        else:
            # Comentario neutro → depende de la satisfacción general
            recomienda = random.random() < (satisfaccion_general / 5.0)

        # Gasto promedio semanal estimado (coherente con precios del menú)
        gasto_base = random.uniform(8.0, 35.0)
        gasto_semanal = round(gasto_base * factor, 2)

        encuesta = {
            "id_encuesta": f"ENC-{i+1:04d}",
            "fecha": fecha,
            "estudiante": {
                "nombre": f"{nombre} {apellido}",
                "genero": genero,
                "carrera": carrera,
                "semestre": semestre,
                "id_estudiante": f"EST-{random.randint(10000, 99999)}"
            },
            "frecuencia_visita": frecuencia,
            "gasto_semanal_estimado_usd": gasto_semanal,
            "producto_mas_consumido": producto_favorito,
            "calificaciones": {
                "calidad_alimentos": calidad_alimentos,
                "variedad_menu": variedad_menu,
                "atencion_servicio": atencion_servicio,
                "relacion_precio_calidad": relacion_precio_calidad,
                "limpieza_ambiente": limpieza_ambiente,
                "satisfaccion_general": satisfaccion_general
            },
            "recomienda_cafeteria": recomienda,
            "comentario": comentario
        }

        # Encuestas del 2do semestre incluyen campo extra: razón de menor frecuencia
        if mes >= 7 and frecuencia in ["1-2 veces por semana", "Ocasionalmente"]:
            encuesta["razon_menor_frecuencia"] = random.choice(razones_menor_frecuencia)

        encuestas.append(encuesta)

    # Ordenar por fecha
    encuestas.sort(key=lambda e: e["fecha"])
    return encuestas


# ================================================================
# 2. GENERADOR DE REPORTES DE PROVEEDORES
# ================================================================
def generar_reportes_proveedores() -> list[dict]:
    """
    Genera un reporte mensual por proveedor (5 proveedores × 12 meses = 60 reportes).
    Los volúmenes de pedido decrecen ~20 % a lo largo del año, coherente
    con la caída en ventas. Los proveedores también registran observaciones
    que reflejan la situación.
    """
    reportes = []

    observaciones_normales = [
        "Entrega puntual, sin novedades.",
        "Pedido completo. Calidad dentro de estándares.",
        "Se realizó verificación de cadena de frío. Todo conforme.",
        "Producto recibido en condiciones óptimas.",
        "Sin novedad. Factura procesada.",
    ]

    observaciones_reduccion = [
        "Se redujo el volumen de pedido respecto al mes anterior por baja demanda.",
        "Cliente solicitó reducir frecuencia de entrega a quincenal.",
        "Se ajustó pedido mínimo por disminución en el consumo.",
        "Volumen menor al proyectado inicialmente para este periodo.",
        "Se reprogramó entrega por exceso de inventario en cafetería.",
    ]

    observaciones_preocupacion = [
        "Pedido considerablemente menor al promedio histórico. Se sugiere reunión con administración.",
        "La cafetería ha solicitado suspender temporalmente la línea de {insumo}.",
        "Se detectaron devoluciones por producto próximo a vencer (bajo rotación).",
        "Volumen mínimo alcanzado. Riesgo de perder condiciones de precio mayorista.",
        "Se negociaron nuevos plazos de pago por flujo de caja reducido del cliente.",
    ]

    meses_nombres = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    report_id = 1
    for proveedor in proveedores:
        # Volumen base mensual (unidades/kg, según proveedor)
        volumen_base = random.randint(120, 350)
        costo_unitario_insumo = round(random.uniform(1.5, 8.0), 2)

        for mes in range(1, 13):
            # Factor de declive para mitad del mes
            mid_month_day = (datetime(2025, mes, 15) - start_date).days
            factor = _decline_factor(min(mid_month_day, days_in_year - 1))

            # Volumen con declive + variación aleatoria ±8%
            variacion = random.uniform(-0.08, 0.08)
            volumen = max(10, int(volumen_base * factor * (1 + variacion)))

            # Entregas del mes
            if mes <= 4:
                entregas_programadas = 4
                entregas_cumplidas = random.choices([4, 3], weights=[0.85, 0.15], k=1)[0]
            elif mes <= 8:
                entregas_programadas = random.choice([3, 4])
                entregas_cumplidas = min(entregas_programadas,
                                         random.choices([entregas_programadas, entregas_programadas - 1],
                                                        weights=[0.7, 0.3], k=1)[0])
            else:
                entregas_programadas = random.choice([2, 3])
                entregas_cumplidas = entregas_programadas  # Menos pedidos pero se cumplen

            # Devoluciones (más frecuentes a fin de año por menor rotación)
            if factor > 0.92:
                pct_devolucion = random.uniform(0, 0.02)
            elif factor > 0.85:
                pct_devolucion = random.uniform(0.01, 0.05)
            else:
                pct_devolucion = random.uniform(0.03, 0.10)
            unidades_devueltas = int(volumen * pct_devolucion)

            costo_total = round(volumen * costo_unitario_insumo, 2)

            # Observaciones
            if factor > 0.92:
                obs = random.choice(observaciones_normales)
            elif factor > 0.85:
                obs = random.choice(observaciones_reduccion)
            else:
                obs_pool = random.choices(
                    [observaciones_reduccion, observaciones_preocupacion],
                    weights=[0.3, 0.7], k=1
                )[0]
                obs = random.choice(obs_pool).format(
                    insumo=random.choice(proveedor["insumos"])
                )

            # Calificación del servicio del proveedor por la cafetería
            calificacion_proveedor = round(random.uniform(3.5, 5.0), 1)
            # La calificación que el proveedor da a la puntualidad de pago de la cafetería
            if factor > 0.90:
                puntualidad_pago = random.choice(["Puntual", "Puntual", "Puntual", "Atraso leve (1-5 días)"])
            elif factor > 0.85:
                puntualidad_pago = random.choice(["Puntual", "Atraso leve (1-5 días)", "Atraso leve (1-5 días)"])
            else:
                puntualidad_pago = random.choice(
                    ["Atraso leve (1-5 días)", "Atraso moderado (6-15 días)",
                     "Atraso leve (1-5 días)", "Atraso moderado (6-15 días)", "Puntual"]
                )

            fecha_reporte = datetime(2025, mes, 28) if mes != 2 else datetime(2025, 2, 28)

            reporte = {
                "id_reporte": f"RPT-{report_id:04d}",
                "fecha_reporte": fecha_reporte.strftime("%Y-%m-%d"),
                "mes": meses_nombres[mes - 1],
                "anio": 2025,
                "proveedor": {
                    "nombre": proveedor["nombre"],
                    "nit": proveedor["nit"],
                    "contacto": proveedor["contacto"],
                    "categoria": proveedor["categoria"]
                },
                "insumos_suministrados": proveedor["insumos"],
                "productos_cafeteria_asociados": proveedor["productos_cafeteria"],
                "volumen_pedido": {
                    "unidades_solicitadas": volumen,
                    "unidades_devueltas": unidades_devueltas,
                    "unidades_netas": volumen - unidades_devueltas,
                    "costo_unitario_promedio_usd": costo_unitario_insumo,
                    "costo_total_usd": costo_total
                },
                "entregas": {
                    "programadas": entregas_programadas,
                    "cumplidas": entregas_cumplidas,
                    "tasa_cumplimiento": round(entregas_cumplidas / entregas_programadas * 100, 1)
                },
                "puntualidad_pago_cafeteria": puntualidad_pago,
                "calificacion_servicio_proveedor": calificacion_proveedor,
                "observaciones": obs,
                "factor_demanda_relativo": round(factor, 3)
            }
            reportes.append(reporte)
            report_id += 1

    # Ordenar por fecha
    reportes.sort(key=lambda r: r["fecha_reporte"])
    return reportes


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    random.seed(42)  # Reproducibilidad

    # Generar encuestas
    encuestas = generar_encuestas(n=2400)
    with open("encuestas_estudiantes.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "descripcion": "Encuestas de satisfacción aplicadas a estudiantes de la cafetería universitaria durante 2025",
                "total_encuestas": len(encuestas),
                "periodo": "2025-01-01 a 2025-12-31",
                "nota": "Las calificaciones y comentarios reflejan un deterioro progresivo coherente con la caída del ~20% en ventas registrada en ventas_cafeteria.csv"
            },
            "encuestas": encuestas
        }, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] encuestas_estudiantes.json generado ({len(encuestas)} encuestas)")

    # Generar reportes de proveedores
    reportes = generar_reportes_proveedores()
    with open("reportes_proveedores.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "descripcion": "Reportes mensuales de proveedores de la cafetería universitaria durante 2025",
                "total_reportes": len(reportes),
                "periodo": "2025-01-01 a 2025-12-31",
                "proveedores": [p["nombre"] for p in proveedores],
                "nota": "Los volúmenes de pedido decrecen ~20% linealmente a lo largo del año, reflejando la caída en ventas. Los campos de devoluciones y observaciones también reflejan la situación."
            },
            "reportes": reportes
        }, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] reportes_proveedores.json generado ({len(reportes)} reportes)")

    print("\n[INFO] Resumen de coherencia con ventas_cafeteria.csv:")
    print(f"   - Menú: {len(products)} productos (mismos nombres y precios)")
    print(f"   - Periodo: 2025-01-01 -> 2025-12-31")
    print(f"   - Declive: {DECLINE_START:.0%} -> {DECLINE_END:.0%} (lineal)")
    print(f"   - Encuestas: sentimiento se degrada progresivamente")
    print(f"   - Proveedores: volúmenes de pedido bajan ~20%")
