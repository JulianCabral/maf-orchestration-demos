# 01 · Sequential (redactor → revisor → editor)

Tres agentes en cadena: cada uno recibe la conversación acumulada del anterior y la mejora.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- Hay pasos con dependencia clara (borrador → revisión → versión final).
- Cada etapa refina el trabajo de la anterior.

**Evitalo cuando:**
- Las etapas son independientes (usá Concurrent).
- No se sabe de antemano el orden (usá Handoff o Magentic).

## Qué hace la demo

`SequentialBuilder` encadena Redactor, Revisor y Editor sobre el lanzamiento de NovaDesk Assist 2.0. El log didáctico muestra qué agente habla y por qué.

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/01-sequential/src/sequential-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```


Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Redactá el anuncio de lanzamiento de NovaDesk Assist 2.0"}'
```


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren credenciales y **no se ejecutaron** en este repo:

```powershell
cd demos/01-sequential
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Redactá el anuncio de lanzamiento de NovaDesk Assist 2.0"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).
