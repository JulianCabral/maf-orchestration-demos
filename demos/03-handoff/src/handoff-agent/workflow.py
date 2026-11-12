"""Demo 03 - Handoff: triage deriva a facturación / técnico / reembolsos."""

from agent_framework_orchestrations import HandoffBuilder

from shared.agents import crear_especialista, crear_triage

AREAS = ("facturacion", "tecnico", "reembolsos")


def _termina(conversacion) -> bool:
    """Termina cuando el cliente se despide."""
    ultimo = next((m for m in reversed(conversacion) if m.role == "user"), None)
    return bool(ultimo and any(p in ultimo.text.lower() for p in ("gracias", "chau", "eso es todo")))


def crear_workflow():
    triage = crear_triage()
    especialistas = {a: crear_especialista(a) for a in AREAS}
    builder = (
        HandoffBuilder(
            name="handoff_soporte",
            participants=[triage, *especialistas.values()],
            termination_condition=_termina,
        )
        .with_start_agent(triage)
        .add_handoff(triage, list(especialistas.values()))
    )
    # Los especialistas pueden devolver el caso a triage si no es de su área.
    for e in especialistas.values():
        builder = builder.add_handoff(e, [triage])
    return builder.build()
