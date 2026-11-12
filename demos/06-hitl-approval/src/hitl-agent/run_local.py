"""Demo 06 en local (simulado): flujo APROBAR, flujo RECHAZAR y reanudación desde un checkpoint.

python run_local.py
"""

import asyncio
import tempfile

from agent_framework import FileCheckpointStorage

from shared.dominio import CONSULTA_CLIENTE_REEMBOLSO
from shared.logging_didactico import configurar_consola, ejecutar_con_log, log, titulo
from workflow import crear_workflow

RAZONES = {"ejecutor_reembolso": "propone el reembolso y se detiene a pedir aprobación antes de mover dinero."}


async def flujo(decision: str, titulo_flujo: str) -> None:
    titulo(titulo_flujo)
    wf = crear_workflow()
    log("sistema", f"Cliente: {CONSULTA_CLIENTE_REEMBOLSO}")
    pendientes = await ejecutar_con_log(wf, CONSULTA_CLIENTE_REEMBOLSO, razones=RAZONES)
    pedido = pendientes[0]
    log("pedido", pedido.data["mensaje"])
    log("sistema", f"Supervisor responde: {decision!r}")
    await ejecutar_con_log(wf, None, razones=RAZONES, responses={pedido.request_id: decision})


async def flujo_con_checkpoint() -> None:
    """Simula un reinicio: la pausa se guarda en disco y otra instancia del workflow la retoma."""
    titulo("Flujo 3 · La pausa sobrevive a un reinicio (checkpoint en disco)")
    with tempfile.TemporaryDirectory() as carpeta:
        storage = FileCheckpointStorage(carpeta)
        wf1 = crear_workflow(checkpoint_storage=storage)
        pendientes = await ejecutar_con_log(wf1, CONSULTA_CLIENTE_REEMBOLSO, razones=RAZONES)
        ultimo = await storage.get_latest(workflow_name=wf1.name)
        log("sistema", f"Checkpoint guardado: {ultimo.checkpoint_id[:8]}… (el 'proceso' se reinicia ahora)")
        del wf1
        wf2 = crear_workflow(checkpoint_storage=storage)
        log("sistema", "Supervisor responde: 'aprobar' (a un proceso nuevo, que retoma el checkpoint)")
        await ejecutar_con_log(
            wf2, None, razones=RAZONES, checkpoint_id=ultimo.checkpoint_id, responses={pendientes[0].request_id: "aprobar"}
        )


async def main() -> None:
    configurar_consola()
    await flujo("aprobar", "Flujo 1 · APROBAR → la herramienta sensible se ejecuta")
    await flujo("rechazar: el monto no coincide con el pedido", "Flujo 2 · RECHAZAR → no se mueve dinero")
    await flujo_con_checkpoint()


if __name__ == "__main__":
    asyncio.run(main())
