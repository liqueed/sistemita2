"""Commontags registers."""

# Django
from django import template

# Utilities
import os

register = template.Library()


@register.filter
def filename(value):
    """Retorna el nombre de un archivo."""
    return os.path.basename(value.file.name)
