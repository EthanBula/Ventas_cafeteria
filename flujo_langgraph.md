# Arquitectura y Flujo de LangGraph - Cafetería

A continuación se detalla la arquitectura del agente conversacional para la cafetería universitaria, basado en LangGraph.

## Diagrama del Flujo

```mermaid
graph TD
    %% Nodos principales
    Start((Inicio)) --> Router{"router_node<br/>(Clasificador de intención)"}
    
    %% Ramas condicionales
    Router -->|Clasificación: 'ventas'| Sales["sales_analyst<br/>(Especialista en Transacciones)"]
    Router -->|Clasificación: 'proveedores'| Supplier["supplier_analyst<br/>(Evaluador de Suministros)"]
    Router -->|Clasificación: 'satisfaccion'| Survey["survey_analyst<br/>(Voz del Cliente)"]
    Router -->|Clasificación: 'estrategico'| Strategic["strategic_synthesizer<br/>(Consultor de Alto Nivel)"]
    Router -->|Clasificación: 'general'| General["general_responder<br/>(Manejo de Out-of-Scope)"]
    
    %% Convergencia
    Sales --> Formatter["response_formatter<br/>(Estructuración y Markdown)"]
    Supplier --> Formatter
    Survey --> Formatter
    Strategic --> Formatter
    General --> Formatter
    
    %% Fin
    Formatter --> End((Fin))

    %% Estilos Visuales
    classDef startEnd fill:#252525,stroke:#888,stroke-width:2px,color:#fff;
    classDef router fill:#2b5278,stroke:#4a90e2,stroke-width:2px,color:#fff;
    classDef analyst fill:#1e4620,stroke:#4caf50,stroke-width:2px,color:#fff;
    classDef synthesizer fill:#5c2b66,stroke:#ab47bc,stroke-width:2px,color:#fff;
    classDef formatter fill:#7a4013,stroke:#ff9800,stroke-width:2px,color:#fff;

    class Start,End startEnd;
    class Router router;
    class Sales,Supplier,Survey,General analyst;
    class Strategic synthesizer;
    class Formatter formatter;
```

## Explicación del Flujo Paso a Paso

1. **Entrada (`__start__`)**: El usuario (el director o coordinador de la cafetería) envía un mensaje o pregunta en lenguaje natural desde la interfaz desarrollada en Reflex.
2. **Clasificación Condicional (`router_node`)**: El sistema utiliza un LLM rápido/ligero para clasificar la intención de la consulta en 1 de 5 dominios predefinidos. Esto evita enviar contexto irrelevante al modelo en los pasos posteriores y ahorra tokens.
3. **Nodos Especialistas (El Análisis)**: Según el resultado del Router, el estado del grafo se enruta a un experto:
   - **`sales_analyst`**: Analiza caídas de ingresos, productos más vendidos, y métricas transaccionales basado en los datos del punto de venta.
   - **`supplier_analyst`**: Evalúa entregas de proveedores, calidad y problemas de abastecimiento en la cadena de suministro.
   - **`survey_analyst`**: Examina el _feedback_ cualitativo y cuantitativo de las encuestas estudiantiles.
   - **`strategic_synthesizer`**: Se activa para preguntas ejecutivas o planes de acción. Toma en cuenta el cruce de los 3 dominios de datos para encontrar correlaciones (ej. *¿Afectan las demoras del proveedor "Lácteos San Miguel" a las ventas matutinas del Capuccino?*).
   - **`general_responder`**: Resuelve consultas genéricas o saludos, evitando gastar recursos analíticos en preguntas que no corresponden a métricas.
4. **Formateo de la Salida (`response_formatter`)**: Independientemente del especialista que haya procesado la información, el resultado confluye en este nodo. Aquí se le da un formato estructurado y pulido (con tablas, métricas destacadas y recomendaciones accionables) de nivel ejecutivo.
5. **Fin (`__end__`)**: El agente finaliza su estado y se envía la respuesta formateada de vuelta al historial conversacional.
