# 06 · Human-in-the-loop (aprobación de reembolso)

Una herramienta sensible (`emitir_reembolso`) NO se ejecuta hasta que una persona aprueba. El workflow se pausa con `ctx.request_info()` y se reanuda con un `@response_handler`.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- Acciones irreversibles o con impacto financiero.
- Se requiere auditoría de quién aprobó qué.

**Evitalo cuando:**
- Acciones de bajo riesgo (la aprobación sólo agrega fricción).

## Qué hace la demo

`EjecutorReembolso` corre al analista, que propone el reembolso; luego `request_info` pausa. Si la persona responde `aprobar` se llama a `emitir_reembolso`; con `rechazar: motivo` se cierra sin ejecutar. También acepta sí/no o JSON.

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/06-hitl-approval/src/hitl-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```

`run_local.py` muestra tres escenarios: aprobar, rechazar y **reanudar desde un checkpoint en disco** con una instancia nueva del workflow (simula un reinicio).

Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Quiero que me devuelvan el dinero del pedido NV-1042"}'
```

**Flujo HTTP (probado local):**

1. `POST /responses` con el pedido → la respuesta trae un `function_call` llamado `request_info` (el `call_id` es el id de la solicitud, con pedido, monto y motivo).
2. Aprobar o rechazar: `POST /responses` con `previous_response_id` y `input: [{"type":"function_call_output","call_id":"<call_id>","output":"aprobar"}]` (o `"rechazar: monto incorrecto"`).
3. La respuesta final es el mensaje "Reembolso emitido…" o "RECHAZADO…".


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren credenciales y **no se ejecutaron** en este repo:

```powershell
cd demos/06-hitl-approval
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Quiero que me devuelvan el dinero del pedido NV-1042"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).

## HITL en hosted agents: dos vías

Guía oficial: <https://learn.microsoft.com/azure/foundry/agents/how-to/add-human-in-the-loop> y <https://learn.microsoft.com/agent-framework/workflows/human-in-the-loop>.

**(a) Vía principal (implementada aquí): workflow MAF + Responses.** `ctx.request_info()` / `@response_handler`; el host usa `ResponsesServerOptions(resilient_background=True)` y persiste un checkpoint en el punto de interrupción, de modo que la pausa sobrevive a reinicios del contenedor. `request_info` aparece como `function_call` y se responde con `function_call_output`.

**Variante de aprobación de herramienta**: con `approval_mode="always_require"` en la tool, el host emite `mcp_approval_request` y se responde con un `mcp_approval_response` (`approve: true/false`).

**(b) Alternativa (no implementada, sólo documentada): `@multi_turn_task`** de `azure.ai.agentserver.core.tasks`. La tarea se suspende bajo un `task_id` y re-entra con `entry_mode == "resumed"` cuando llega la decisión. Útil si no usás workflows MAF.

## Qué se probó local y qué requiere Foundry

| Aspecto | Local (simulado) | Requiere Foundry |
|---|---|---|
| Pausa con `request_info`, aprobar, rechazar | Sí (`run_local.py`) | - |
| Reanudar desde checkpoint de disco | Sí (`FileCheckpointStorage`) | - |
| Host Responses, `function_call` → `function_call_output` | Sí (`python main.py`, puerto 8088) | - |
| Checkpoint/estado durable entre reinicios del contenedor | Parcial (disco local) | Sí: almacenamiento del host en Foundry |
| Modelo real, identidad administrada, trazas | No | Sí |
| `azd provision` / `azd deploy` | No ejecutado | Sí |

## Notas

- `request_data` es un `dict` plano a propósito: los dataclasses propios en checkpoints se bloquean ("Checkpoint deserialization blocked") salvo que configures `allowed_checkpoint_types`.
- La versión actual de `agent-framework-foundry-hosting` (beta) marca como deprecado pasar un `WorkflowAgent` como `agent=`; se mantiene `as_agent()` por ser lo que usan los samples oficiales. La alternativa es `workflow=<factory>` más `parse_response`.
