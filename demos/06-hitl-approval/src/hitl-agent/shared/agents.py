"""Agentes comunes y personas simuladas (respuestas deterministas en español).

Cada ``crear_*`` devuelve un ``Agent`` de MAF. En modo simulado la "persona" produce la respuesta;
en modo real (Foundry / Azure OpenAI) el mismo agente usa solo sus ``instructions``.
"""

from __future__ import annotations

import json
from typing import Any

from agent_framework import Agent, Message

from .chat_client import get_chat_client
from .dominio import BASE_CONOCIMIENTO, PRODUCTO


def _ultimo_texto(msgs: list[Message], rol: str | None = None) -> str:
    for m in reversed(msgs):
        if rol is None or m.role == rol:
            if m.text:
                return m.text
    return ""


def _primer_usuario(msgs: list[Message]) -> str:
    for m in msgs:
        if m.role == "user" and m.text:
            return m.text
    return ""


def _agente(nombre: str, instrucciones: str, persona, descripcion: str = "", tools: list | None = None, **extra) -> Agent:
    return Agent(
        get_chat_client(persona),
        instructions=instrucciones,
        name=nombre,
        description=descripcion or instrucciones.split(".")[0],
        tools=tools,
        **extra,
    )


# --------------------------------------------------------------------------- 01 / 04: redacción

def crear_redactor() -> Agent:
    def persona(msgs, _o):
        tarea = _primer_usuario(msgs)
        feedback = [m.text for m in msgs if m.role == "assistant" and m.author_name in ("critico", "revisor")]
        if feedback:
            return (
                f"Borrador v2 (incorporo la crítica: «{feedback[-1][:70]}…»): "
                f"{PRODUCTO} reduce el tiempo de primera respuesta y deriva a una persona cuando el caso lo requiere. "
                "Incluyo un ejemplo concreto y un llamado a la acción claro."
            )
        return (
            f"Borrador v1: Presentamos {PRODUCTO}, el asistente de IA que resuelve consultas de soporte en segundos "
            f"y deriva a una persona los casos complejos. (Tarea: {tarea[:60]}…)"
        )

    return _agente(
        "redactor",
        "Sos un redactor de comunicaciones. Escribí un borrador breve, claro y en español.",
        persona,
        "Redacta el borrador del comunicado.",
    )


def crear_revisor() -> Agent:
    def persona(_m, _o):
        return (
            "Revisión: el mensaje es claro, pero falta un dato concreto (p. ej. % de reducción de tiempos) "
            "y aclarar cuándo interviene una persona. Tono correcto."
        )

    return _agente(
        "revisor", "Sos un revisor crítico. Señalá mejoras concretas en 2 frases.", persona, "Revisa el borrador."
    )


def crear_editor() -> Agent:
    def persona(msgs, _o):
        return (
            f"VERSIÓN FINAL — {PRODUCTO}: resolvé hasta un 40% más de consultas en el primer contacto. "
            "Cuando el caso es complejo, una persona de tu equipo toma el control sin perder el contexto. "
            "¡Probalo hoy!"
        )

    return _agente("editor", "Sos un editor. Integrá las correcciones y entregá la versión final.", persona, "Edita la versión final.")


def crear_critico() -> Agent:
    def persona(msgs, _o):
        versiones = sum(1 for m in msgs if m.author_name == "redactor")
        if versiones <= 1:
            return "Crítica: falta un ejemplo concreto y un llamado a la acción. Reescribí incorporando ambos."
        return "APROBADO: el comunicado es claro, concreto y tiene llamado a la acción."

    return _agente(
        "critico",
        "Sos un crítico editorial. Si el texto está bien respondé 'APROBADO'; si no, da una crítica concreta.",
        persona,
        "Critica el borrador y aprueba cuando esté listo.",
    )


# --------------------------------------------------------------------------- 02: analistas

def crear_analista(area: str) -> Agent:
    textos = {
        "costos": "Costos: inversión inicial estimada USD 120k (licencias + integración); ahorro operativo ~USD 8k/mes.",
        "riesgos": "Riesgos: respuestas incorrectas de la IA, privacidad de datos de clientes y resistencia interna al cambio.",
        "marketing": "Marketing: mensaje 'IA que libera a tu equipo', webinar de lanzamiento y casos de éxito de 2 clientes piloto.",
    }
    return _agente(
        f"analista_{area}",
        f"Sos un analista de {area}. Respondé en una o dos frases desde esa perspectiva.",
        lambda _m, _o: textos[area],
        f"Analiza {area}.",
    )


# --------------------------------------------------------------------------- 03: handoff

def _herramienta_handoff(opts: dict[str, Any], clave: str) -> str | None:
    for t in opts.get("tools") or []:
        nombre = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
        if nombre and clave in nombre:
            return nombre
    return None


def crear_triage() -> Agent:
    def persona(msgs, opts):
        if any(c.type == "function_result" for m in msgs for c in m.contents):
            return "Te derivé con el equipo indicado."
        t = _primer_usuario(msgs).lower()
        destino = None
        if any(k in t for k in ("devuelv", "reembols", "dinero")):
            destino = "reembolsos"
        elif any(k in t for k in ("cobr", "factura", "suscrip")):
            destino = "facturacion"
        elif any(k in t for k in ("app", "error", "cierra", "falla")):
            destino = "tecnico"
        if destino and (nombre := _herramienta_handoff(opts, destino)):
            return ("tool", nombre, {})
        return "Contame un poco más: ¿es sobre facturación, un problema técnico o un reembolso?"

    return _agente(
        "triage",
        "Sos el agente de triage de soporte. Derivá a facturacion, tecnico o reembolsos con la herramienta de handoff. "
        "Si no está claro, preguntá.",
        persona,
        "Recibe al cliente y lo deriva.",
        require_per_service_call_history_persistence=True,
    )


def crear_especialista(area: str) -> Agent:
    textos = {
        "facturacion": "Facturación: revisé tu cuenta y veo un cargo duplicado del mes. Lo anulo y verás el crédito en 3-5 días.",
        "tecnico": "Soporte técnico: es un bug conocido en Android 14. Actualizá a la versión 2.0.3; si persiste, te escalo.",
        "reembolsos": "Reembolsos: registré tu solicitud del pedido NV-1042 y se la paso a un supervisor para su aprobación.",
    }
    return _agente(
        area,
        f"Sos el especialista de {area} de {PRODUCTO}. Resolvé la consulta del cliente en español.",
        lambda _m, _o: textos[area],
        f"Atiende consultas de {area}.",
        require_per_service_call_history_persistence=True,
    )


# --------------------------------------------------------------------------- 05: magentic

def crear_investigador() -> Agent:
    def persona(msgs, _o):
        return f"Hallazgos: {BASE_CONOCIMIENTO['metricas']} {BASE_CONOCIMIENTO['costos']}"

    return _agente("investigador", "Sos un investigador. Reuní datos relevantes y citá la fuente.", persona, "Busca información y datos.")


def crear_coder() -> Agent:
    def persona(msgs, _o):
        ahorro = 5000 * 0.40 * 4
        return (
            "```python\ntickets, pct, costo = 5000, 0.40, 4\nprint(tickets * pct * costo)\n```\n"
            f"Resultado: ahorro mensual estimado = USD {ahorro:,.0f}"
        )

    return _agente("coder", "Sos un analista que calcula con código Python y reporta el resultado.", persona, "Hace cálculos con código.")


def persona_manager_magentic(participantes: list[str]):
    """Persona del manager de Magentic: reconoce los 4 prompts del StandardMagenticManager y devuelve JSON válido."""
    estado = {"turno": 0}

    def persona(msgs, _o):
        texto = _ultimo_texto(msgs, "user")
        if "GIVEN OR VERIFIED FACTS" in texto or "pre-survey" in texto:
            return "1. HECHOS DADOS: 5000 tickets, 40% automatizado, USD 4 por ticket.\n2. A INVESTIGAR: métricas de soporte.\n3. A CALCULAR: ahorro mensual."
        if "bullet-point plan" in texto:
            return f"- {participantes[0]}: reunir métricas y costos\n- {participantes[1]}: calcular el ahorro mensual\n- Redactar la respuesta final"
        if "is_request_satisfied" in texto:
            estado["turno"] += 1
            if estado["turno"] == 1:
                nombre, instr, ok = participantes[0], "Reuní las métricas de soporte relevantes y los costos por ticket.", False
            elif estado["turno"] == 2:
                nombre, instr, ok = participantes[1], "Calculá el ahorro mensual con los datos obtenidos.", False
            else:
                nombre, instr, ok = participantes[1], "Listo.", True
            r = lambda a, why: {"reason": why, "answer": a}
            return json.dumps(
                {
                    "is_request_satisfied": r(ok, "Ya tenemos datos y cálculo" if ok else "Falta información"),
                    "is_in_loop": r(False, "No hay repetición"),
                    "is_progress_being_made": r(True, "Cada turno aporta algo nuevo"),
                    "next_speaker": r(nombre, f"{nombre} es el indicado para el siguiente paso"),
                    "instruction_or_question": r(instr, "Instrucción para el siguiente agente"),
                }
            )
        return (
            "Respuesta final: seguí TPR, FCR, CSAT y % de autoresolución. "
            "Con 5000 tickets, 40% automatizado a USD 4 → ahorro de USD 8.000 por mes."
        )

    return persona


# --------------------------------------------------------------------------- 06: reembolsos

def crear_analista_reembolsos() -> Agent:
    """Analiza el pedido del cliente y devuelve SOLO una propuesta en JSON (no ejecuta nada)."""

    def persona(msgs, _o):
        return json.dumps({"pedido": "NV-1042", "monto": 120.0, "motivo": "producto dañado"})

    return _agente(
        "analista_reembolsos",
        'Analizá el pedido del cliente y respondé SOLO JSON: {"pedido": str, "monto": number, "motivo": str}.',
        persona,
        "Propone un reembolso (no lo ejecuta).",
    )


