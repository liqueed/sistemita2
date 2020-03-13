#language:es
Característica: Ahorra mucho trabajo conciliar de manera automática

Escenario: Pago de un cliente (liqueed cobra)
Dado que "OSDE" es cliente referenciado como "O.s.d.e." en el resumen bancario con CUIT "30546741253"
Cuando se facture desde liqueed "500" pesos el "3/1/2010" al cliente "OSDE" con "0" pesos de gastos
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "6968308", concepto "Pago Proveedores Interbanking Exte  - O.s.d.e. 30546741253 03 6968308", importe "500,00" y saldo "0,00"
Y se concilian movimientos pendientes automáticamente
Entonces está registrado un pago de cliente a liqueed que asocia la última factura con el último movimiento

@wip
Escenario: Pago a un consultor (liqueed paga)
Dado que el consultor "David" tiene la siguiente estrategia tributaria
    | CUIT        | CBU                    |
    | 24270501601 | 1500035000008161431046 |
    | 27272255747 | 0070066530004021386186 |
Y que "BIND" es cliente referenciado como "BIND" en el resumen bancario con CUIT "30546741253"
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "BIND" con "0" pesos de gastos
Y el único consultor sea "David"
Y que decide facturar los "850" pesos que le corresponden con esta estrategia
    | CUIT        | Monto |
    | 24270501601 | 400   |
    | 27272255747 | 450   |
Y se produjo el movimiento del "04/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "7181803", concepto "Pago Proveedores Interbanking Exte  - BIND 30546741253 03 7181803", importe "1000" y saldo "0"
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "0824", referencia "004096801", concepto "Pago Cci 24hs Gravada Interbanking  - A Cbu 1500035000008161431046 ", importe "400" y saldo "791997.54"
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "0824", referencia "004093464", concepto "Pago Cci 24hs Gravada Interbanking  - A Cbu 0070066530004021386186 ", importe "450" y saldo "1035530,86"
Y se concilian movimientos pendientes automáticamente
Entonces el consultor "David" ya no tiene delivery pendiente de cobro

Escenario: Impuesto al cheque por débitos y créditos
Cuando se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "4633", referencia "000002292", concepto "Imp Ley 25413 Deb 0,6% 	", importe "-1452" y saldo "791997.54"
Y se produjo el movimiento del "04/02/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "4637", referencia "000002285", concepto "Imp Ley 25413 Cred 0,6% 	", importe "-1421" y saldo "1035530,86"
Y se concilian movimientos pendientes automáticamente
Entonces el total pagado por impuesto al cheque hasta el momento es "2873"