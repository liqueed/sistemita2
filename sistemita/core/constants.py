"""Módulo de Constantes."""

# No modificar el orden
MONEDAS = (('P', '$'), ('D', 'USD'))


TIPOS_FACTURA = (
    ('A', 'A'),
    ('ARETEN', 'A SUJETA A RETENCIÓN'),
    ('B', 'B'),
    ('C', 'C'),
    ('RC', 'Recibo C'),  # Nuevo
    ('E', 'E'),  # Nuevo
    ('FCPYME', 'FC PYME'),
    ('M', 'M'),
    ('NCA', 'NC A'),
    ('NCARETEN', 'NC A SUJETA A RETENCION'),
    ('NCB', 'NC B'),
    ('NCC', 'NC C'),
    ('NCFCPYME', 'NC FCPYME'),
    ('NCM', 'NC M'),
)


TIPOS_FACTURA_IMPORT = (
    ('1 - Factura A', 'A'),
    ('6 - Factura B', 'B'),
    ('11 - Factura C', 'C'),
    ('15 - Recibo C', 'Recibo C'),
    ('19 - Factura de Exportación E', 'E'),
    ('201 - Factura de Crédito Electrónica MyPyMEs (FCE) A', 'FC PYME'),
    ('51 - Facturas M', 'M'),
    ('3 - Nota de Crédito A', 'NC A'),
    ('12 - Nota de Crédito B', 'NC B'),
    ('13 - Nota de Crédito C', 'NC C'),
    ('203 - Nota de Crédito Electrónica MyPyMEs (FCE) A', 'NC FCPYME'),
    ('53 - Nota de Crédito M', 'NC M'),
)

TIPOS_DOC_IMPORT = 'CUIT'
