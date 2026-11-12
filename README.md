# maf-orchestration-demos

Demos en español de **orquestación de agentes con Microsoft Agent Framework (Python)**, listos para desplegar como *hosted agents* en Microsoft Foundry. Dominio común: soporte al cliente y lanzamiento de **NovaDesk Assist 2.0**.

## ¿Qué patrón elegir?

| Necesito… | Patrón | Demo |
|---|---|---|
| Pasos en orden fijo, cada uno refina al anterior | Sequential | [01-sequential](demos/01-sequential) |
| Varias perspectivas independientes en paralelo y consolidarlas | Concurrent | [02-concurrent](demos/02-concurrent) |
| Derivar al especialista correcto; conversación multi-turno | Handoff | [03-handoff](demos/03-handoff) |
| Iterar entre agentes (redactor/crítico) con control de turnos | Group Chat | [04-group-chat](demos/04-group-chat) |
| Tarea abierta: un manager planifica y delega | Magentic | [05-magentic](demos/05-magentic) |
| Que una persona apruebe una acción sensible | Human-in-the-loop | [06-hitl-approval](demos/06-hitl-approval) |

## Inicio rápido (sin credenciales)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r demos/01-sequential/src/sequential-agent/requirements.txt
cd demos/01-sequential/src/sequential-agent
python run_local.py
```

Todas las demos usan por defecto un **cliente de chat simulado** (determinista, sin red). Cada `run_local.py` imprime un log didáctico: qué agente habla y por qué.

## Cliente de chat intercambiable (`CHAT_CLIENT`)

| Valor | Qué usa | Variables |
|---|---|---|
| `simulated` (default) | Cliente simulado | – |
| `foundry` | `FoundryChatClient` | `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME` |
| `azure_openai` | `OpenAIChatClient` sobre Azure OpenAI | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME` |

La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry). El modo `azure_openai` no fue verificado contra un recurso real.

## Estructura

```
shared/                 # cliente de chat, agentes comunes, logging didáctico (fuente única)
scripts/sync_shared.py  # copia shared/ en cada demo (--check para verificar)
demos/NN-xxx/
  azure.yaml            # servicio hosted agent (azd ai agent)
  README.md
  src/<agente>/         # workflow.py, run_local.py, main.py, Dockerfile, requirements.txt, shared/ (copia)
```

Cada demo es autocontenida porque el contenedor sólo ve su carpeta `src/<agente>`. Después de editar `shared/` ejecutá `python scripts/sync_shared.py`.

## Despliegue en Foundry

Cada demo envuelve el workflow como agente (`workflow.as_agent()`) y lo sirve con `ResponsesHostServer` (protocolo Responses; 03 y 06 usan `resilient_background` para multi-turno y aprobaciones). Los pasos (`azd ai agent init`, `azd provision`, `azd deploy`) están en el README de cada demo. Versiones probadas: ver `requirements.txt`.

## Estado de verificación

Probado con azd 1.37.x, extensión `azure.ai.agents` y `gpt-4.1-mini` (GlobalStandard, eastus2):

| Qué | Resultado |
|---|---|
| Las 6 demos en local con modelo real (`CHAT_CLIENT=foundry`) | OK |
| `azd provision` + `azd deploy` + `azd ai agent invoke` de 01, 03 y 06 | OK |
| 06 HITL hosted: pausa (`request_info`) y reanudación con `function_call_output` = `aprobar` | OK, usando `background: true` (la pausa no es reanudable en modo streaming) |
| 02, 04 y 05 desplegadas | No probadas (misma plantilla que 01) |

Hallazgos que importan al desplegar:

- `azure.yaml` usa el bloque plano (sin `config:`) y el protocolo `responses` **2.0.0**; con 1.0.0 el host falla con «require a trusted user ID and call ID».
- 03 y 06 necesitan `CheckpointStoreProvider(allowed_checkpoint_types=["types:GenericAlias"])`; sin eso el checkpoint falla al deserializar.
- Tu usuario necesita el rol **Foundry User** (y OpenAI User) en la cuenta; la propagación de RBAC puede tardar unos minutos.
- `agent-framework-foundry-hosting` es beta y avisa que `as_agent()` está deprecado a favor de `workflow=` con `parse_response`.
