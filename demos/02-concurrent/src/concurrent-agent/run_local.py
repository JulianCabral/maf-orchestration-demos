"""Demo 02 en local (cliente simulado por defecto): python run_local.py ["tarea"]"""

import asyncio
import sys

from shared.dominio import TAREA_EVALUACION
from shared.logging_didactico import configurar_consola, ejecutar_con_log, log, titulo
from workflow import crear_workflow

RAZONES = {f"analista_{a}": "corre EN PARALELO con los otros analistas (fan-out)." for a in ("costos", "riesgos", "marketing")}


async def main() -> None:
    configurar_consola()
    tarea = sys.argv[1] if len(sys.argv) > 1 else TAREA_EVALUACION
    titulo("Demo 02 · Concurrente (costos ∥ riesgos ∥ marketing → agregador)")
    print(f"Tarea: {tarea}\n")
    await ejecutar_con_log(crear_workflow(), tarea, razones=RAZONES)
    log("sistema", "El agregador (fan-in) combinó las 3 respuestas en un único informe.")


if __name__ == "__main__":
    asyncio.run(main())
