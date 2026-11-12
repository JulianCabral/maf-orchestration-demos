# 02 · Concurrent (analistas en paralelo + agregador)

Tres analistas (costos, riesgos, marketing) trabajan a la vez sobre la misma consulta y un agregador consolida las respuestas.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- Perspectivas independientes sobre la misma entrada.
- Se busca menor latencia total.

**Evitalo cuando:**
- Un paso necesita la salida de otro (usá Sequential).
- Hay conflictos que requieren debate (usá Group Chat).

## Qué hace la demo

`ConcurrentBuilder(...).with_aggregator(fn)` hace fan-out/fan-in; el agregador arma un resumen ejecutivo.

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/02-concurrent/src/concurrent-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```


Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Evaluá el lanzamiento de NovaDesk Assist 2.0"}'
```


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren credenciales y **no se ejecutaron** en este repo:

```powershell
cd demos/02-concurrent
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Evaluá el lanzamiento de NovaDesk Assist 2.0"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).
