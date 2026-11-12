"""Logging didáctico: muestra qué agente habla y por qué, a partir de los eventos del workflow."""

from __future__ import annotations

import sys
from typing import Any

ICONOS = {"turno": "🗣️", "razon": "💡", "salida": "✅", "pedido": "⏸️", "sistema": "⚙️"}
_INTERNOS = {"input-conversation", "end", "end-conversation"}


def configurar_consola() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def titulo(texto: str) -> None:
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


def log(tipo: str, texto: str) -> None:
    print(f"{ICONOS.get(tipo, '•')} {texto}")


def texto_de(data: Any) -> str:
    """Extrae texto legible de los distintos tipos de datos que circulan por un workflow."""
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    if isinstance(data, (list, tuple)):
        return " | ".join(dict.fromkeys(t for t in (texto_de(d) for d in data) if t))
    ar = getattr(data, "agent_response", None)
    if ar is not None:
        return ar.text or ""
    t = getattr(data, "text", None)
    return t if isinstance(t, str) else ""


def corto(texto: str, n: int = 160) -> str:
    texto = " ".join(texto.split())
    return texto if len(texto) <= n else texto[: n - 1] + "…"


_ULTIMO: dict[str, str] = {}


def _turno(ejecutor: str, texto: str, razones: dict[str, str]) -> None:
    if _ULTIMO.get(ejecutor) == texto:
        return  # evita repetir un turno ya mostrado (p. ej. al reanudar tras una pausa)
    _ULTIMO[ejecutor] = texto
    if ejecutor in razones:
        log("razon", f"{ejecutor} habla porque: {razones[ejecutor]}")
    log("turno", f"[{ejecutor}] {corto(texto)}")


async def ejecutar_con_log(workflow: Any, entrada: Any, *, razones: dict[str, str] | None = None, **kwargs: Any) -> list[Any]:
    """Corre el workflow en streaming imprimiendo quién habla y por qué.

    ``razones`` mapea id de agente -> por qué interviene (se imprime antes de su turno).
    Devuelve los eventos ``request_info`` pendientes (vacío si el workflow terminó).
    """
    razones = razones or {}
    pendientes: list[Any] = []
    buffer: dict[str, str] = {}

    def vaciar() -> None:
        for ejecutor, txt in list(buffer.items()):
            if txt.strip() and ejecutor not in _INTERNOS:
                _turno(ejecutor, txt, razones)
        buffer.clear()

    async for ev in workflow.run(entrada, stream=True, **kwargs):
        tipo = ev.type
        ejecutor = getattr(ev, "executor_id", None) or ""
        if tipo == "output":
            buffer[ejecutor] = buffer.get(ejecutor, "") + texto_de(ev.data)
        elif tipo == "executor_completed" and ejecutor not in _INTERNOS:
            txt = buffer.pop(ejecutor, "") or texto_de(ev.data)
            if txt.strip():
                _turno(ejecutor, txt, razones)
        elif tipo == "request_info":
            vaciar()
            pendientes.append(ev)
            log("pedido", f"El workflow PAUSA y espera a una persona (request_id={corto(str(ev.request_id), 12)}).")
        elif tipo == "handoff_sent":
            log("sistema", f"HANDOFF: {ev.data.source} → {ev.data.target}")
        elif tipo == "data" and ev.data is not None:
            nombre = type(ev.data).__name__
            if nombre.endswith("Event"):
                log("sistema", f"{nombre}: {corto(str(ev.data), 200)}")
        elif ev.data is not None and type(ev.data).__name__ == "MagenticOrchestratorEvent":
            d = ev.data
            if d.event_type.value == "plan_created":
                log("sistema", f"PLAN del manager: {corto(texto_de(d.content), 220)}")
            elif d.event_type.value == "progress_ledger_updated" and hasattr(d.content, "next_speaker"):
                c = d.content
                if c.is_request_satisfied.answer:
                    log("razon", f"Manager: tarea cumplida ({c.is_request_satisfied.reason}). Arma la respuesta final.")
                else:
                    log("razon", f"Manager elige a «{c.next_speaker.answer}»: {c.next_speaker.reason} → {corto(str(c.instruction_or_question.answer), 120)}")
        elif ev.data is not None and type(ev.data).__name__ == "GroupChatRequestSentEvent":
            log("sistema", f"Ronda {ev.data.round_index}: se le da la palabra a {ev.data.participant_name}")
    vaciar()
    return pendientes


