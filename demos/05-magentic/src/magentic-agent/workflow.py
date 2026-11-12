"""Demo 05 - Magentic: un manager planifica y coordina a investigador + coder."""

from agent_framework import Agent
from agent_framework_orchestrations import MagenticBuilder, StandardMagenticManager

from shared.agents import crear_coder, crear_investigador, persona_manager_magentic
from shared.chat_client import get_chat_client


def crear_workflow():
    investigador, coder = crear_investigador(), crear_coder()
    manager_agent = Agent(
        get_chat_client(persona_manager_magentic([investigador.name, coder.name])),
        instructions="Sos el manager de un equipo: planificás, elegís quién habla y decidís cuándo terminar.",
        name="manager",
    )
    manager = StandardMagenticManager(manager_agent, max_round_count=6, max_stall_count=2)
    return MagenticBuilder(
        name="magentic_investigacion",
        participants=[investigador, coder],
        manager=manager,
    ).build()
