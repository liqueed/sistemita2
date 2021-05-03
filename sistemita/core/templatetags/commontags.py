"""Commontags registers."""

# Utilities
import os

# Django
from django import template

register = template.Library()


@register.filter
def filename(value):
    """Retorna el nombre de un archivo."""
    return os.path.basename(value.file.name)
