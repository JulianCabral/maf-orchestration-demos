"""Demo 03 en local: conversación multi-turno simulada con handoffs.

python run_local.py                 # recorre las 3 consultas de ejemplo
python run_local.py "tu consulta"   # una consulta propia
"""

import asyncio
import sys

from agent_framework_orchestrations import HandoffAgentUserRequest

from shared.dominio import CONSULTA_CLIENTE_FACTURACION, CONSULTA_CLIENTE_REEMBOLSO, CONSULTA_CLIENTE_TECNICA
from shared.logging_didactico import configurar_consola, ejecutar_con_log, log, titulo
from workflow import crear_workflow

RAZONES = {
    "triage": "es la puerta de entrada: clasifica la consulta.",
    "facturacion": "triage detectó un tema de cobros/facturas y le hizo handoff.",
    "tecnico": "triage detectó un problema técnico y le hizo handoff.",
    "reembolsos": "triage detectó un pedido de devolución y le hizo handoff.",
}


async def conversar(consulta: str) -> None:
    wf = crear_workflow()
    log("sistema", f"Cliente: {consulta}")
    pendientes = await ejecutar_con_log(wf, consulta, razones=RAZONES)
    # El workflow pausa cada vez que un agente responde sin hacer handoff: hay que devolverle el turno al usuario.
    if pendientes and isinstance(pendientes[0].data, HandoffAgentUserRequest):
        log("sistema", "Cliente: Gracias, eso es todo.")
        resp = HandoffAgentUserRequest.create_response("Gracias, eso es todo.")
        await ejecutar_con_log(wf, None, razones=RAZONES, responses={pendientes[0].request_id: resp})


async def main() -> None:
    configurar_consola()
    consultas = [sys.argv[1]] if len(sys.argv) > 1 else [
        CONSULTA_CLIENTE_FACTURACION,
        CONSULTA_CLIENTE_TECNICA,
        CONSULTA_CLIENTE_REEMBOLSO,
    ]
    for c in consultas:
        titulo("Demo 03 · Handoff (triage → especialista)")
        await conversar(c)


if __name__ == "__main__":
    asyncio.run(main())
