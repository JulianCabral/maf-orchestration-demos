"""Demo 01 en local (cliente simulado por defecto): python run_local.py ["tarea"]"""

import asyncio
import sys

from shared.dominio import TAREA_LANZAMIENTO
from shared.logging_didactico import configurar_consola, ejecutar_con_log, titulo
from workflow import crear_workflow

RAZONES = {
    "redactor": "es el primero de la cadena: produce el borrador.",
    "revisor": "recibe TODO lo anterior y lo critica.",
    "editor": "es el último: integra la crítica y entrega la versión final.",
}


async def main() -> None:
    configurar_consola()
    tarea = sys.argv[1] if len(sys.argv) > 1 else TAREA_LANZAMIENTO
    titulo("Demo 01 · Secuencial (redactor → revisor → editor)")
    print(f"Tarea: {tarea}\n")
    await ejecutar_con_log(crear_workflow(), tarea, razones=RAZONES)


if __name__ == "__main__":
    asyncio.run(main())
