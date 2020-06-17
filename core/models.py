from django.db import models


class TimeStampedModel(models.Model):
    creado = models.DateTimeField('Creado', editable=False, blank=True, auto_now_add=True)
    modificado = models.DateTimeField('Modificado', editable=False, blank=True, auto_now=True)

    class Meta:
        get_latest_by = 'modificado'
        abstract = True


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


class Departamento(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    provincia = models.ForeignKey(Provincia, verbose_name='Provincia', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ('nombre',)

    def __str__(self):
        return '{}'.format(self.nombre)

    def __unicode__(self):
        return self.__str__()


class Localidad(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    departamento = models.ForeignKey(Departamento, null=True, verbose_name='Departamento', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
        ordering = ('nombre',)

    def __str__(self):
        return '{0}'.format(self.name)

    def __unicode__(self):
        return self.__str__()


class Cliente(TimeStampedModel, models.Model):
    FORMAS_ENVIO = (
        ('C', 'Correo'),
        ('U', 'Link')
    )
    razon_social = models.CharField('Razón Social', blank=False, null=False, max_length=128)
    cuit = models.CharField('CUIT', blank=False, null=False, max_length=11)
    correo = models.EmailField(blank=False)
    calle = models.CharField('Calle', max_length=35, blank=True)
    numero = models.CharField('Número', max_length=12, blank=True)
    piso = models.CharField('Piso', max_length=4, blank=True)
    dpto = models.CharField('Departamento', max_length=4, blank=True)
    localidad = models.ForeignKey(Localidad, null=True, blank=True, verbose_name='Localidad', on_delete=models.SET_NULL)
    #orden_compra
    tipo_envio_factura = models.CharField(blank=False, null=False, verbose_name='Forma de envio de factura', choices=FORMAS_ENVIO, max_length=1)
    link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ('razon_social', )
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'


class Proveedor(TimeStampedModel, models.Model):
    razon_social = models.CharField('Razón Social', blank=False, null=False, max_length=128)
    cuit = models.CharField('CUIT', blank=False, null=False, max_length=11)
    correo = models.EmailField(blank=False)
    calle = models.CharField('Calle', max_length=35, blank=True)
    numero = models.CharField('Número', max_length=12, blank=True)
    piso = models.CharField('Piso', max_length=4, blank=True)
    dpto = models.CharField('Departamento', max_length=4, blank=True)
    localidad = models.ForeignKey(Localidad, null=True, blank=True, verbose_name='Localidad', on_delete=models.SET_NULL)
    cbu = models.CharField(max_length=22, blank=True, null=True, verbose_name='CBU')
    # servicio

    class Meta:
        ordering = ('razon_social', )
        verbose_name = 'proveedor'
        verbose_name_plural = 'proveedores'

