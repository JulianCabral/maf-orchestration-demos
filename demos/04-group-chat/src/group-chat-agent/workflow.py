"""Demo 04 - Group chat: redactor + crítico con dos estrategias de selección de turno."""

import os

from agent_framework_orchestrations import GroupChatBuilder, GroupChatState

from shared.agents import crear_critico, crear_redactor


def seleccion_round_robin(estado: GroupChatState) -> str:
    """Turnos rotativos: redactor, crítico, redactor, crítico…"""
    nombres = list(estado.participants.keys())
    return nombres[estado.current_round % len(nombres)]


def seleccion_custom(estado: GroupChatState) -> str:
    """Selector con lógica propia: después de hablar el redactor siempre toca el crítico;
    después del crítico vuelve el redactor (solo si no aprobó; si aprobó termina la condición)."""
    ultimo = estado.conversation[-1] if estado.conversation else None
    if ultimo is not None and ultimo.author_name == "redactor":
        return "critico"
    return "redactor"


def _aprobado(conversacion) -> bool:
    ultimo = conversacion[-1] if conversacion else None
    return bool(ultimo and ultimo.author_name == "critico" and "APROBADO" in (ultimo.text or ""))


def crear_workflow(modo: str | None = None):
    modo = modo or os.environ.get("GROUP_CHAT_MODE", "selector")
    seleccion = seleccion_round_robin if modo == "round_robin" else seleccion_custom
    return GroupChatBuilder(
        name=f"group_chat_{modo}",
        participants=[crear_redactor(), crear_critico()],
        selection_func=seleccion,
        termination_condition=_aprobado,
        max_rounds=8,
    ).build()
