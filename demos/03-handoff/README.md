# 03 · Handoff (triage → facturación / técnico / reembolsos)

Un agente de triage deriva la conversación al especialista adecuado; el control pasa de uno a otro y el usuario sigue hablando con el especialista.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- El especialista correcto depende del mensaje del usuario.
- Conversaciones multi-turno con cambio de responsable.

**Evitalo cuando:**
- El orden es fijo (Sequential).
- Se necesita un plan dinámico con manager (Magentic).

## Qué hace la demo

`HandoffBuilder` con triage y tres especialistas. Cuando un especialista responde sin derivar, el workflow emite un `request_info` (`HandoffAgentUserRequest`) y espera el siguiente turno del usuario. Termina cuando el usuario se despide.

Nota: todos los participantes requieren `require_per_service_call_history_persistence=True`.

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/03-handoff/src/handoff-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```


Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Me cobraron dos veces la suscripción"}'
```

**Multi-turno**: la respuesta contiene un `function_call` `request_info`. Respondé con otra llamada a `/responses` usando `previous_response_id` y un `function_call_output` (`call_id` = id del pedido, `output` = tu texto). El host corre con `resilient_background=True` y restaura el checkpoint.


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren credenciales y **no se ejecutaron** en este repo:

```powershell
cd demos/03-handoff
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Me cobraron dos veces la suscripción"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).

Protocolo: Responses (necesario para el multi-turno por `previous_response_id`).
