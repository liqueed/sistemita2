#language: es
Característica: Distintas maneras de recibir pagos por parte de clientes

Escenario: Pago de cliente directamente a cuenta bancaria de liqueed por el total de una factura
Dado que "Kiosquito" es cliente
Cuando se facture desde liqueed "500" pesos el "03/01/2010" al cliente "Kiosquito" con "0" pesos de gastos
Y el cliente "Kiosquito" pague la ultima factura por transferencia bancaria el "04/01/2010"
Entonces el cliente "Kiosquito" adeuda "0" pesos