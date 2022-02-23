"""Archivos factories."""

# Fake
import factory
from factory.django import DjangoModelFactory

# Sitemita
from sistemita.core.models import Archivo


class ArchivoFactory(DjangoModelFactory):
    """Fabrica del modelo de archivos."""

    class Meta:
        """Factory settings."""

        model = Archivo

    documento = factory.django.FileField(filename='document.pdf')
