#language:es
Característica: Ahorra mucho trabajo conciliar de manera automática

Escenario: Pago de un cliente (liqueed cobra)
Dado que "OSDE" es cliente referenciado como "O.s.d.e." en el resumen bancario con CUIT "30546741253"
Cuando se facture desde liqueed "500" pesos el "3/1/2010" al cliente "OSDE" con "0" pesos de gastos
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "6968308", concepto "Pago Proveedores Interbanking Exte  - O.s.d.e. 30546741253 03 6968308", importe "500,00" y saldo "0,00"
Y se concilian movimientos pendientes automáticamente
Entonces está registrado un pago de cliente a liqueed que asocia la última factura con el último movimiento

Escenario: Impuesto al cheque por débitos y créditos
Cuando se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "4633", referencia "000002292", concepto "Imp Ley 25413 Deb 0,6% 	", importe "-1452" y saldo "791997.54"
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "4637", referencia "000002285", concepto "Imp Ley 25413 Cred 0,6% 	", importe "-1421" y saldo "1035530,86"
Y se concilian movimientos pendientes automáticamente
Entonces el total pagado por impuesto al cheque hasta el momento es "2873"