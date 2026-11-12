"""Demo 04 en local: corre las dos estrategias (round-robin y selector custom).

python run_local.py ["tarea"]
"""

import asyncio
import sys

from shared.dominio import TAREA_LANZAMIENTO
from shared.logging_didactico import configurar_consola, ejecutar_con_log, titulo
from workflow import crear_workflow

RAZONES = {
    "redactor": "el selector le dio el turno para escribir o reescribir el borrador.",
    "critico": "el selector le dio el turno para evaluar el último borrador.",
}


async def main() -> None:
    configurar_consola()
    tarea = sys.argv[1] if len(sys.argv) > 1 else TAREA_LANZAMIENTO
    for modo, desc in (("round_robin", "turnos rotativos fijos"), ("selector", "función de selección custom")):
        titulo(f"Demo 04 · Group chat — {modo} ({desc})")
        await ejecutar_con_log(crear_workflow(modo), tarea, razones=RAZONES)


if __name__ == "__main__":
    asyncio.run(main())
