"""Commontags registers."""

# Django
from django import template

# Utilities
import os

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)
