#language: es
Característica: El sistema calcula automáticamente la retención del impuesto a las ganancias que se aplica cuando liqueed paga a un proveedor

Escenario: Pago único menor al monto no imponible de 67170 pesos
Dado que se facturó "100" pesos + IVA al cliente "Prisma" 
Y que el consultor "Alan" le facturó a liqueed "100" pesos + IVA correspondientes a la última factura hecha a un cliente
Cuando se le quiera pagar "100" pesos al consultor "Alan" correspondientes a la última factura hecha a liqueed
Entonces la retención de ganancias correspondiente al último pago habrá sido de "0" pesos