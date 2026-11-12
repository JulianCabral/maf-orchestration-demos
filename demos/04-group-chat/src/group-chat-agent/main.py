"""Entrypoint del hosted agent (protocolo Responses). Envuelve el workflow como agente.

Estrategia de selección: variable de entorno GROUP_CHAT_MODE = selector (default) | round_robin.
"""

from agent_framework_foundry_hosting import ResponsesHostServer

from workflow import crear_workflow


def main() -> None:
    ResponsesHostServer(crear_workflow().as_agent()).run()


if __name__ == "__main__":
    main()
