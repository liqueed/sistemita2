"""Commontags registers."""

# Utilities
import os

# Django
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def filename(value):
    """Retorna el nombre de un archivo."""
    return os.path.basename(value.file.name)


@register.simple_tag
def get_setting(name):
    """Retorna las settings."""
    return getattr(settings, name, None)
