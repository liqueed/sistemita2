#language:es
Característica: Registro del pago de impuesto al cheque, tanto por débitos como por créditos

Escenario: Cliente paga por transferencia a liqueed. See debe pagar 0,6% de impuesto al crédito
Dado que "Kiosquito" es cliente
Cuando se facture desde liqueed "500" pesos el "03/01/2010" al cliente "Kiosquito" con "0" pesos de gastos
Y el cliente "Kiosquito" pague la ultima factura por transferencia bancaria el "04/01/2010"
Y se pague "3" pesos de impuesto al cheque por crédito por el último pago de un cliente
Entonces el total pagado por impuesto al cheque hasta el momento es "3"