"""Demo 02 - Concurrente: analistas de costos / riesgos / marketing + agregador."""

from agent_framework import Message
from agent_framework_orchestrations import ConcurrentBuilder

from shared.agents import crear_analista


async def agregar(resultados) -> str:
    """Agregador determinista: une las respuestas de todos los analistas en un solo informe."""
    partes = []
    for r in resultados:
        msgs = r.agent_response.messages
        texto = msgs[-1].text if msgs else ""
        partes.append(f"- {r.executor_id}: {texto}")
    return "Informe consolidado del lanzamiento:\n" + "\n".join(partes)


def crear_workflow():
    analistas = [crear_analista(a) for a in ("costos", "riesgos", "marketing")]
    return ConcurrentBuilder(participants=analistas, name="concurrente_analisis").with_aggregator(agregar).build()
