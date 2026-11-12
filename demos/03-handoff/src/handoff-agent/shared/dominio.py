"""Dominio común de los demos: soporte al cliente / lanzamiento de producto.

Producto ficticio: **NovaDesk Assist 2.0**, un asistente de IA para equipos de soporte.
"""

PRODUCTO = "NovaDesk Assist 2.0"

# Tareas de ejemplo por patrón (se pueden sobreescribir por línea de comandos).
TAREA_LANZAMIENTO = (
    f"Redactá un comunicado para clientes anunciando el lanzamiento de {PRODUCTO}, "
    "un asistente de IA que resuelve consultas de soporte y deriva casos complejos a personas."
)
TAREA_EVALUACION = (
    f"Evaluá el lanzamiento de {PRODUCTO} en el mercado de LATAM: "
    "inversión inicial, riesgos principales y plan de comunicación."
)
CONSULTA_CLIENTE_FACTURACION = "Hola, me cobraron dos veces la suscripción de este mes y no entiendo la factura."
CONSULTA_CLIENTE_TECNICA = "La app se cierra sola cada vez que abro el panel de reportes en Android."
CONSULTA_CLIENTE_REEMBOLSO = "Quiero que me devuelvan el dinero del pedido NV-1042, el producto llegó dañado."
TAREA_INVESTIGACION = (
    f"Investigá qué métricas de soporte conviene seguir tras lanzar {PRODUCTO} "
    "y calculá el ahorro mensual si se automatiza el 40% de 5000 tickets a USD 4 por ticket."
)

# Base de conocimiento simulada que usan las herramientas locales de los demos.
BASE_CONOCIMIENTO = {
    "metricas": (
        "Métricas clave de soporte: tiempo de primera respuesta (TPR), tasa de resolución en primer contacto (FCR), "
        "CSAT y porcentaje de tickets autoresueltos por IA."
    ),
    "costos": "Costo promedio por ticket atendido por una persona: USD 4. Por la IA: USD 0,6.",
    "politica_reembolsos": "Reembolsos hasta USD 500 con aprobación de un supervisor; por encima, requiere gerencia.",
}
