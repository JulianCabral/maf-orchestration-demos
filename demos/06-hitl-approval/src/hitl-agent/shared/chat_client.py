"""Cliente de chat intercambiable.

Por defecto (``CHAT_CLIENT=simulated``) usa un cliente determinista que no necesita credenciales.
Con ``CHAT_CLIENT=foundry`` usa Foundry y con ``CHAT_CLIENT=azure_openai`` usa Azure OpenAI,
siempre con ``DefaultAzureCredential`` (identidad administrada cuando corre en Foundry).
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from agent_framework import (
    BaseChatClient,
    ChatMiddlewareLayer,
    ChatResponse,
    ChatResponseUpdate,
    Content,
    FunctionInvocationLayer,
    Message,
    ResponseStream,
)

# Una "persona" recibe el historial y las herramientas disponibles y devuelve
# texto, o una llamada a herramienta ("tool", nombre, argumentos).
Persona = Callable[[list[Message], dict[str, Any]], "str | tuple[str, str, dict[str, Any]]"]


class SimulatedChatClient(FunctionInvocationLayer, ChatMiddlewareLayer, BaseChatClient):
    """Cliente simulado: responde según una persona determinista (sin red, sin credenciales)."""

    def __init__(self, persona: Persona) -> None:
        super().__init__()
        self._persona = persona

    def _contents(self, messages: Sequence[Message], options: dict[str, Any]) -> list[Content]:
        salida = self._persona(list(messages), options)
        if isinstance(salida, str):
            return [Content.from_text(salida)]
        _, nombre, argumentos = salida
        return [Content.from_function_call(f"call_{nombre}", nombre, arguments=argumentos)]

    def _inner_get_response(self, *, messages: Sequence[Message], stream: bool, options: Any, **kwargs: Any) -> Any:
        contenidos = self._contents(messages, dict(options or {}))
        if stream:

            async def _gen():
                yield ChatResponseUpdate(role="assistant", contents=contenidos)

            return ResponseStream(_gen(), finalizer=ChatResponse.from_updates)

        async def _resp() -> ChatResponse:
            return ChatResponse(messages=[Message(role="assistant", contents=contenidos)])

        return _resp()


def modo_cliente() -> str:
    return os.environ.get("CHAT_CLIENT", "simulated").strip().lower()


def get_chat_client(persona: Persona | None = None) -> Any:
    """Devuelve el cliente de chat según ``CHAT_CLIENT``.

    ``persona`` solo se usa en modo simulado; en modo real el comportamiento lo define
    el modelo con las instrucciones del agente.
    """
    modo = modo_cliente()
    if modo == "simulated":
        if persona is None:
            raise ValueError("El modo simulado necesita una persona.")
        return SimulatedChatClient(persona)

    from azure.identity import DefaultAzureCredential

    if modo == "foundry":
        from agent_framework.foundry import FoundryChatClient

        return FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            credential=DefaultAzureCredential(),
        )
    if modo == "azure_openai":
        from agent_framework.openai import OpenAIChatClient

        return OpenAIChatClient(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            credential=DefaultAzureCredential(),
        )
    raise ValueError(f"CHAT_CLIENT desconocido: {modo!r} (usar simulated | foundry | azure_openai)")
