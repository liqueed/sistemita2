"""Modelos de entidades territoriales."""

# Django
from django.db import models


class Pais(models.Model):
    """Modelo País."""

    codigo = models.CharField(primary_key=True, max_length=3, verbose_name='Código')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    class Meta:
        """Configuraciones del modelo."""

        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ('nombre',)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return u'{0}'.format(self.nombre)

    def __unicode__(self):
        """Devuelve una representación en string del modelo."""
        return self.__str__()


class Provincia(models.Model):
    """Modelo Provincia."""

    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    class Meta:
        """Configuraciones del modelo."""

        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return '{}'.format(self.nombre)

    def __unicode__(self):
        """Devuelve una representación en string del modelo."""
        return self.__str__()


class Distrito(models.Model):
    """Modelo Distrito."""

    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    provincia = models.ForeignKey(Provincia, verbose_name='Provincia', on_delete=models.CASCADE)

    class Meta:
        """Configuraciones del modelo."""

        verbose_name = 'Distrito'
        verbose_name_plural = 'Distritos'
        ordering = ('nombre',)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return '{}'.format(self.nombre)

    def __unicode__(self):
        """Representación en cadena del modelo."""
        return self.__str__()


class Localidad(models.Model):
    """Modelo Localidad."""

    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    distrito = models.ForeignKey(Distrito, null=True, verbose_name='Distrito', on_delete=models.CASCADE)

    class Meta:
        """Configuraciones del modelo."""

        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
        ordering = ('nombre',)

    def __str__(self):
        """Devuelve un representación legible del modelo."""
        return '{0}'.format(self.nombre)

    def __unicode__(self):
        """Representación en cadena del modelo."""
        return self.__str__()
