"""Entrypoint del hosted agent (Responses). El handoff es multi-turno: cada pausa vuelve al cliente.

`resilient_background=True` permite que la conversación sobreviva a reinicios del contenedor
(requiere checkpoints; ver README).
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
