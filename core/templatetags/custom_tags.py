from django import template

register = template.Library()

@register.filter
def times(number):
    return range(int(number))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@register.filter
def endswith(value, suffix):
    """
    Filtro para verificar si una cadena termina con un sufijo.
    Uso en template: {{ archivo.name|endswith:'.pdf' }}
    """
    if isinstance(value, str):
        return value.lower().endswith(suffix.lower())
    return False

@register.filter
def startswith(value, prefix):
    """
    Filtro para verificar si una cadena comienza con un prefijo.
    """
    if isinstance(value, str):
        return value.lower().startswith(prefix.lower())
    return False