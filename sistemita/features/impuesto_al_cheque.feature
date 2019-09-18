#language:es
Característica: Registro del pago de impuesto al cheque, tanto por débitos como por créditos

Escenario: Cliente paga por transferencia a liqueed. See debe pagar 0,6% de impuesto al crédito
Dado que "Kiosquito" es cliente
Cuando se facture desde liqueed "500" pesos el "03/01/2010" al cliente "Kiosquito" con "0" pesos de gastos
Y se produjo el movimiento del "04/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "7181803", concepto "Pago Proveedores Interbanking Exte  - Kiosquito 30546741253 03 7181803", importe "500" y saldo "0"
Y se concilia la última factura con el último movimiento bancario 
Y se pague "3" pesos de impuesto al cheque por crédito por el último pago de un cliente
Entonces el total pagado por impuesto al cheque hasta el momento es "3"