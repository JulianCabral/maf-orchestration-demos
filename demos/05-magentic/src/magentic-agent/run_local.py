"""Demo 05 en local: el manager (simulado) arma el plan y reparte el trabajo.

python run_local.py ["tarea"]
"""

import asyncio
import sys

from shared.dominio import TAREA_INVESTIGACION
from shared.logging_didactico import configurar_consola, ejecutar_con_log, titulo
from workflow import crear_workflow

RAZONES = {
    "investigador": "el manager lo eligió en su ledger de progreso para reunir datos.",
    "coder": "el manager lo eligió para calcular con los datos ya reunidos.",
}


async def main() -> None:
    configurar_consola()
    tarea = sys.argv[1] if len(sys.argv) > 1 else TAREA_INVESTIGACION
    titulo("Demo 05 · Magentic (manager → investigador / coder)")
    print(f"Tarea: {tarea}\n")
    await ejecutar_con_log(crear_workflow(), tarea, razones=RAZONES)


if __name__ == "__main__":
    asyncio.run(main())
