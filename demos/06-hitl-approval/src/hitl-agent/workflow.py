"""Demo 06 - Human-in-the-loop: un reembolso NO se emite hasta que una persona lo aprueba.

Vía principal (a): executor con ``ctx.request_info()`` + ``@response_handler``.
El workflow se PAUSA en ``request_info``; al hospedarlo con Responses el pedido llega al cliente como
un ``function_call`` llamado ``request_info`` y se reanuda con un ``function_call_output``.
"""

from __future__ import annotations

import json
from typing import Any

from agent_framework import Executor, Message, WorkflowBuilder, WorkflowContext, handler, response_handler
from typing_extensions import Never

from shared.agents import crear_analista_reembolsos

LIMITE_SUPERVISOR_USD = 500.0


def emitir_reembolso(pedido: str, monto: float, motivo: str) -> str:
    """HERRAMIENTA SENSIBLE: mueve dinero. Solo se invoca después de una aprobación humana."""
    return f"Reembolso emitido: pedido {pedido}, USD {monto:,.2f} ({motivo})."


def interpretar_decision(respuesta: Any) -> tuple[bool, str]:
    """Acepta 'aprobar', 'rechazar: motivo', 'sí/no' o un JSON {"aprobado": bool, "comentario": str}."""
    if isinstance(respuesta, dict):
        return bool(respuesta.get("aprobado")), str(respuesta.get("comentario", ""))
    texto = str(respuesta).strip()
    if texto.startswith("{"):
        try:
            return interpretar_decision(json.loads(texto))
        except json.JSONDecodeError:
            pass
    bajo = texto.lower()
    aprobado = bajo.startswith(("aprob", "si", "sí", "ok", "yes", "true"))
    return aprobado, texto


class EjecutorReembolso(Executor):
    """Propone un reembolso, pausa para pedir aprobación y solo entonces ejecuta la herramienta."""

    def __init__(self) -> None:
        super().__init__(id="ejecutor_reembolso")
        self._analista = crear_analista_reembolsos()
        self._auditoria: list[str] = []

    @handler
    async def iniciar(self, mensajes: str | list[Message], ctx: WorkflowContext[Never, str]) -> None:
        if isinstance(mensajes, str):
            consulta = mensajes
        else:
            consulta = " ".join(m.text for m in mensajes if m.role == "user" and m.text)
        propuesta = json.loads((await self._analista.run(consulta)).text)
        # Tipos básicos (dict): se serializan sin configuración extra en los checkpoints.
        solicitud = {
            "pedido": propuesta["pedido"],
            "monto": float(propuesta["monto"]),
            "motivo": propuesta["motivo"],
            "mensaje": (
                f"¿Aprobás el reembolso de USD {propuesta['monto']:,.2f} del pedido {propuesta['pedido']} "
                f"({propuesta['motivo']})? Respondé 'aprobar' o 'rechazar: <motivo>'."
            ),
        }
        self._auditoria.append(f"propuesto:{solicitud['pedido']}")
        # El workflow queda en pausa aquí hasta que llegue la respuesta humana.
        await ctx.request_info(request_data=solicitud, response_type=str)

    @response_handler
    async def al_decidir(
        self, solicitud: dict[str, Any], respuesta: str, ctx: WorkflowContext[Never, str]
    ) -> None:
        aprobado, comentario = interpretar_decision(respuesta)
        if aprobado:
            self._auditoria.append(f"aprobado:{solicitud['pedido']}")
            await ctx.yield_output(emitir_reembolso(solicitud["pedido"], solicitud["monto"], solicitud["motivo"]))
        else:
            self._auditoria.append(f"rechazado:{solicitud['pedido']}")
            await ctx.yield_output(
                f"Reembolso del pedido {solicitud['pedido']} RECHAZADO por la persona revisora. {comentario}".strip()
            )

    async def on_checkpoint_save(self) -> dict[str, Any]:
        return {"auditoria": self._auditoria}

    async def on_checkpoint_restore(self, estado: dict[str, Any]) -> None:
        self._auditoria = list(estado.get("auditoria", []))


def crear_workflow(checkpoint_storage=None):
    return WorkflowBuilder(
        name="hitl_reembolsos",
        description="Reembolsos con aprobación humana antes de mover dinero.",
        start_executor=EjecutorReembolso(),
        checkpoint_storage=checkpoint_storage,
    ).build()
