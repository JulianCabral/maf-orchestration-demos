# 04 · Group Chat (redactor + crítico)

Redactor y crítico iteran sobre un texto hasta que el crítico responde APROBADO.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- Refinamiento iterativo con feedback cruzado.
- Querés controlar quién habla (round-robin o selector propio).

**Evitalo cuando:**
- Pasos sin iteración (Sequential).
- Tareas abiertas con herramientas (Magentic).

## Qué hace la demo

`GroupChatBuilder` con dos modos: `round_robin` y `selector` (función `selection_func(GroupChatState)` propia). `run_local.py` corre ambos; el host usa `GROUP_CHAT_MODE` (`selector` | `round_robin`).

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/04-group-chat/src/group-chat-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```


Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Escribí un anuncio breve de NovaDesk Assist 2.0"}'
```


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren una suscripción de Azure con cuota para el modelo (ver README raíz, «Estado de verificación»):

```powershell
cd demos/04-group-chat
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Escribí un anuncio breve de NovaDesk Assist 2.0"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).

Variable opcional del despliegue: `GROUP_CHAT_MODE` (`selector` por defecto).
