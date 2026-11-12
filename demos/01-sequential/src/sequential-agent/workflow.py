"""Demo 01 - Secuencial: redactor -> revisor -> editor."""

from agent_framework_orchestrations import SequentialBuilder

from shared.agents import crear_editor, crear_redactor, crear_revisor


def crear_workflow():
    return SequentialBuilder(
        name="secuencial_comunicado",
        participants=[crear_redactor(), crear_revisor(), crear_editor()],
    ).build()
