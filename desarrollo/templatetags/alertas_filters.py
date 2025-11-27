from django import template

register = template.Library()

@register.filter
def agrupa_alertas(alertas):
    """
    Filtro de ejemplo: simplemente retorna la lista tal cual.
    Puedes personalizar la lógica de agrupación aquí.
    """
    return alertas

@register.filter
def ejemplo_alerta(value):
    """Filtro de ejemplo para alertas (no hace nada)."""
    return value
