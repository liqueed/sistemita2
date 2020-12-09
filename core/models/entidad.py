from django.db import models


class Pais(models.Model):
    codigo = models.CharField(primary_key=True, max_length=3, verbose_name='Código')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ('nombre',)

    def __str__(self):
        return u'{0}'.format(self.nombre)

    def __unicode__(self):
        return self.__str__()


class Provincia(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'

    def __str__(self):
        return '{}'.format(self.nombre)

    def __unicode__(self):
        return self.__str__()


class Distrito(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    provincia = models.ForeignKey(Provincia, verbose_name='Provincia', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Distrito'
        verbose_name_plural = 'Distritos'
        ordering = ('nombre',)

    def __str__(self):
        return '{}'.format(self.nombre)

    def __unicode__(self):
        return self.__str__()


class Localidad(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    distrito = models.ForeignKey(Distrito, null=True, verbose_name='Distrito', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
        ordering = ('nombre',)

    def __str__(self):
        return '{0}'.format(self.nombre)

    def __unicode__(self):
        return self.__str__()
