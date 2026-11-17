"""
chatapp.py — Interfaz Reflex para el Agente Estratégico de Café du Nord.

Chat UI en Python puro con diseño inspirado en los colores del logo:
azul (#1a3a7a), amarillo (#f2c800), blanco.
"""

import reflex as rx
import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class State(rx.State):
    """Estado de la aplicación Reflex."""

    # Almacenamos mensajes como diccionarios
    messages: list[dict[str, str]] = []
    current_input: str = ""
    is_loading: bool = False

    @rx.event(background=True)
    async def send_message(self):
        """Envía el mensaje del usuario al agente y recibe la respuesta."""
        user_msg = self.current_input
        
        if not user_msg.strip():
            return

        async with self:
            self.messages = self.messages + [{"role": "user", "content": user_msg}]
            self.current_input = ""
            self.is_loading = True

        try:
            from agent.graph import invoke_agent

            response = invoke_agent(user_msg)

            async with self:
                self.messages = self.messages + [{"role": "assistant", "content": response}]
        except Exception as e:
            async with self:
                self.messages = self.messages + [
                    {"role": "assistant", "content": f"⚠️ Error al procesar la consulta: {str(e)}"}
                ]
        finally:
            async with self:
                self.is_loading = False

    def handle_key_down(self, key: str):
        if key == "Enter":
            return State.send_message

    def set_current_input(self, value: str):
        self.current_input = value


def message_bubble(msg: dict[str, str]) -> rx.Component:
    """Renderiza una burbuja de mensaje individual."""
    # En Reflex rx.cond necesita Variables, esto crea comparaciones seguras
    is_user = (msg["role"] == "user")
    content = msg["content"]

    return rx.box(
        rx.box(
            rx.cond(
                is_user,
                rx.text(content, color="white", font_size="0.95em"),
                rx.box(
                    rx.markdown(
                        content,
                        color="#1a1a2e",
                        font_size="0.95em",
                    ),
                ),
            ),
            background=rx.cond(
                is_user,
                "linear-gradient(135deg, #1a3a7a, #2d5fc4)",
                "#f8f9fb",
            ),
            padding="12px 18px",
            border_radius="18px",
            max_width="80%",
            box_shadow="0 1px 3px rgba(0,0,0,0.08)",
            border=rx.cond(
                is_user,
                "none",
                "1px solid #e8e8ee",
            ),
        ),
        display="flex",
        justify_content=rx.cond(is_user, "flex-end", "flex-start"),
        width="100%",
        padding_y="4px",
    )


def chat_area() -> rx.Component:
    """Área de mensajes del chat con scroll."""
    return rx.box(
        rx.cond(
            State.messages.length() == 0,  # type: ignore
            # Estado vacío: mensaje de bienvenida
            rx.center(
                rx.vstack(
                    rx.image(
                        src="/Logos Unidades_Café du Nord (1)-Photoroom.png",
                        width="120px",
                        height="120px",
                        border_radius="50%",
                    ),
                    rx.heading(
                        "Café du Nord",
                        size="6",
                        color="#1a3a7a",
                        font_weight="700",
                    ),
                    rx.text(
                        "Asistente Estratégico",
                        color="#6b7280",
                        font_size="1em",
                    ),
                    rx.text(
                        "Pregúntame sobre ventas, proveedores, satisfacción estudiantil o solicita un análisis estratégico integral.",
                        color="#9ca3af",
                        font_size="0.9em",
                        text_align="center",
                        max_width="400px",
                    ),
                    rx.hstack(
                        rx.badge(
                            "📊 ¿Cómo van las ventas?",
                            variant="surface",
                            color_scheme="blue",
                            size="2",
                        ),
                        rx.badge(
                            "🎯 Plan de acción 90 días",
                            variant="surface",
                            color_scheme="blue",
                            size="2",
                        ),
                        rx.badge(
                            "⭐ Satisfacción estudiantil",
                            variant="surface",
                            color_scheme="blue",
                            size="2",
                        ),
                        spacing="2",
                        flex_wrap="wrap",
                        justify="center",
                    ),
                    spacing="4",
                    align="center",
                    padding_top="80px",
                ),
                width="100%",
                height="100%",
            ),
            # Mensajes
            rx.box(
                rx.foreach(State.messages, message_bubble),
                rx.cond(
                    State.is_loading,
                    rx.box(
                        rx.hstack(
                            rx.spinner(size="2", color="#1a3a7a"),
                            rx.text(
                                "Analizando datos...",
                                color="#6b7280",
                                font_size="0.85em",
                            ),
                            spacing="2",
                        ),
                        padding="12px 18px",
                    ),
                ),
                padding="16px",
                overflow_y="auto",
                flex="1",
            ),
        ),
        flex="1",
        width="100%",
        overflow_y="auto",
        display="flex",
        flex_direction="column",
    )


def input_area() -> rx.Component:
    """Barra de entrada de texto."""
    return rx.box(
        rx.hstack(
            rx.input(
                value=State.current_input,
                on_change=State.set_current_input,
                on_key_down=State.handle_key_down,
                placeholder="Escribe tu pregunta sobre la cafetería...",
                size="3",
                width="100%",
                border_radius="12px",
                variant="surface",
            ),
            rx.button(
                rx.icon("send", size=18),
                on_click=State.send_message,
                loading=State.is_loading,
                size="3",
                border_radius="12px",
                background="linear-gradient(135deg, #1a3a7a, #2d5fc4)",
                cursor="pointer",
                _hover={"opacity": "0.9"},
            ),
            width="100%",
            spacing="3",
        ),
        padding="16px 20px",
        border_top="1px solid #e8e8ee",
        background="white",
        width="100%",
    )


def header() -> rx.Component:
    """Barra superior con logo y nombre."""
    return rx.box(
        rx.hstack(
            rx.image(
                src="/Logos Unidades_Café du Nord (1)-Photoroom.png",
                width="40px",
                height="40px",
                border_radius="50%",
            ),
            rx.vstack(
                rx.heading(
                    "Café du Nord", size="4", color="white", font_weight="700"
                ),
                rx.text(
                    "Agente Estratégico IA",
                    color="rgba(255,255,255,0.8)",
                    font_size="0.75em",
                ),
                spacing="0",
            ),
            rx.spacer(),
            rx.badge(
                "GPT 5.4",
                variant="surface",
                color_scheme="yellow",
                size="1",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        background="linear-gradient(135deg, #1a3a7a 0%, #2d5fc4 100%)",
        padding="12px 20px",
        box_shadow="0 2px 8px rgba(26,58,122,0.15)",
    )


def index() -> rx.Component:
    """Página principal de la aplicación."""
    return rx.box(
        rx.vstack(
            header(),
            chat_area(),
            input_area(),
            spacing="0",
            height="100vh",
            width="100%",
            max_width="1200px",
            margin="0 auto",
            align="stretch",
        ),
        background="#f8f9fb",
        min_height="100vh",
        width="100vw",
    )


# Crear la app
app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
    ),
    style={
        "font_family": "'Inter', 'Segoe UI', sans-serif",
    },
)
app.add_page(index, title="Café du Nord — Agente Estratégico IA")
