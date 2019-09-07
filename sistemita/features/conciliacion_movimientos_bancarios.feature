#language:es
Característica: Para poder cerrar el circuito de pagos y cobros, se asocian movimientos bancarios con las otras operaciones registradas en el sistemita

Escenario: Pago de un cliente (liqueed cobra)
Dado que "OSDE" es cliente
Cuando se facture desde liqueed "500" pesos el "3/1/2010" al cliente "OSDE" con "0" pesos de gastos
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "6968308", concepto "Pago Proveedores Interbanking Exte  - O.s.d.e. 30546741253 03 6968308", importe "500,00" y saldo "0,00"
Y se concilia la última factura con el último movimiento bancario
Entonces está registrado un pago de cliente a liqueed que asocia la última factura con el último movimiento

Escenario: Pago de tarjeta de crédito
Dado que en liqueed hay tarjetas de crédito corporativas "VISA"
Cuando se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "1325", referencia "29797706", concepto "Visa  - Por Deb:05/08/2019 Part 000000000729797706", importe "1000" y saldo "0"
Y se concilia el último movimiento bancario con el último pago de la tarjeta "VISA"
Entonces está registrado un pago de la tarjeta "VISA" con fecha "04/02/2010" por "1000" pesos