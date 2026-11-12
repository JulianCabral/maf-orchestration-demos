# 05 · Magentic (investigador + coder con manager)

Un manager arma un plan, lleva un ledger de progreso y decide quién actúa en cada ronda hasta resolver la tarea.

## Cuándo usarlo / cuándo no

**Usalo cuando:**
- Tareas abiertas que requieren planificar y replanificar.
- Combinación de especialistas (investigación + código).

**Evitalo cuando:**
- Flujos deterministas (Sequential/Concurrent).
- Latencia o costo bajos: el manager agrega llamadas.

## Qué hace la demo

`MagenticBuilder` con `StandardMagenticManager` (`max_round_count`, `max_stall_count`). El log muestra plan, ledger y orden de turnos.

## Correr local (cliente simulado, sin credenciales)

```powershell
cd demos/05-magentic/src/magentic-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_local.py
```


Para usar un modelo real: copiá `.env.example` a `.env` y poné `CHAT_CLIENT=foundry` (o `azure_openai`) con las variables del proyecto. La autenticación usa `DefaultAzureCredential` (az login local, identidad administrada en Foundry).

## Correr como hosted agent en local

```powershell
python main.py          # servidor Responses en http://localhost:8088
curl -s http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Estimá el ahorro anual de NovaDesk Assist 2.0 con 20 agentes"}'
```


## Desplegar en Foundry (hosted agent)

El workflow se expone como agente con `workflow.as_agent()` y `ResponsesHostServer` (`main.py`). Incluye `Dockerfile`, `azure.yaml` y `AGENTS.md`. Estos comandos requieren una suscripción de Azure con cuota para el modelo (ver README raíz, «Estado de verificación»):

```powershell
cd demos/05-magentic
azd ai agent init        # o usá el azure.yaml incluido
azd provision
azd deploy
azd ai agent invoke "Estimá el ahorro anual de NovaDesk Assist 2.0 con 20 agentes"
```

Antes de editar `shared/` en la raíz, ejecutá `python scripts/sync_shared.py` para copiarlo a cada demo (el contenedor sólo ve su propia carpeta).
