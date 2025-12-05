from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='strip_hidden_tags')
def strip_hidden_tags(value):
    """Elimina las etiquetas <a>...</a> vacías que se usan para tracking."""
    if not value:
        return ""
    return re.sub(r'<a href="[^"]*"></a>', '', value)