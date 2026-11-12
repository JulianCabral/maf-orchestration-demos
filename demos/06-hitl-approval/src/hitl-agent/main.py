"""Entrypoint del hosted agent (Responses) con HITL resiliente.

- El workflow se envuelve como agente (`as_agent()`).
- `resilient_background=True`: la ejecución en background sobrevive a reinicios del contenedor.
- El host guarda un checkpoint en el punto de interrupción (`request_info`) y lo restaura al reanudar.
"""

from agent_framework_foundry_hosting import ResponsesHostServer
from azure.ai.agentserver.responses import ResponsesServerOptions

from workflow import crear_workflow


def main() -> None:
    ResponsesHostServer(
        crear_workflow().as_agent(),
        options=ResponsesServerOptions(resilient_background=True),
    ).run()


if __name__ == "__main__":
    main()
