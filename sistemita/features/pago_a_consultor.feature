#language:es
Característica: liqueed le paga a consultor por un trabajo facturado a través de liqueed

Escenario:Un cliente paga por transferencia y el trabajo fue hecho por un solo consultor y el pago de liqueed al consultor es por el total
Dado que "BIND" es cliente
Y que el consultor "David" tiene la siguiente estrategia tributaria
    | CUIT        | CBU                    |
    | 24270501601 | 1500035000008161431046 |
    | 27272255747 | 0070066530004021386186 |
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "BIND" con "0" pesos de gastos
    Y el único consultor sea "David"        
    Y se produjo el movimiento del "04/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "7181803", concepto "Pago Proveedores Interbanking Exte  - BIND 30546741253 03 7181803", importe "1000" y saldo "0"
    Y se concilia la última factura con el último movimiento bancario   
    Y se produjo el movimiento del "05/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "824", referencia "4266732", concepto "Pago Cci 24hs Gravada Interbanking  - A Cbu 1500035000008161431046", importe "850" y saldo "0"
    Y se computa el último movimiento bancario como pago a "David" a su cuenta con CBU "1500035000008161431046" el "05/01/2010" en concepto de delivery asociado a la última factura
Entonces el consultor "David" ya no tiene delivery pendiente de cobro

Escenario:Un cliente paga por transferencia y el trabajo fue hecho por un solo consultor y el pago de liqueed al consultor es parcial
Dado que "BIND" es cliente
Y que el consultor "David" tiene la siguiente estrategia tributaria
    | CUIT        | CBU                    |
    | 24270501601 | 1500035000008161431046 |
    | 27272255747 | 0070066530004021386186 |
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "BIND" con "0" pesos de gastos
    Y el único consultor sea "David"        
    Y se produjo el movimiento del "04/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "2377", referencia "7181803", concepto "Pago Proveedores Interbanking Exte  - BIND 30546741253 03 7181803", importe "1000" y saldo "0"
    Y se concilia la última factura con el último movimiento bancario   
    Y se produjo el movimiento del "05/01/2010" con sucursal de origen código "762" y descripción "Cerrito", código operativo "824", referencia "4266732", concepto "Pago Cci 24hs Gravada Interbanking  - A Cbu 1500035000008161431046", importe "500" y saldo "0"
    Y se computa el último movimiento bancario como pago a "David" a su cuenta con CBU "1500035000008161431046" el "05/01/2010" en concepto de delivery asociado a la última factura
Entonces el saldo bruto disponible de cobro de "David" con liqueed es de "350"

