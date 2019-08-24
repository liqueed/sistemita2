#language:es
Característica: liqueed le paga a consultor por un trabajo facturado a través de liqueed

Escenario:Un cliente paga por transferencia y el trabajo fue hecho por un solo consultor
Dado que "BIND" es cliente
Y que el consultor "David" recibe los pagos en la cuenta con CBU "0123456789012345678901"
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "BIND" con "0" pesos de gastos
    Y el único consultor sea "David"        
    Y el cliente "BIND" pague la ultima factura por transferencia bancaria el "04/01/2010"
    Y liqueed le pague "850" pesos por transferencia a "David" el "05/01/2010" en concepto de delivery 
Entonces el consultor "David" ya no tiene delivery pendiente de cobro