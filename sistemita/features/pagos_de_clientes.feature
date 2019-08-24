#language: es
Característica: Distintas maneras de recibir pagos por parte de clientes

Escenario: Pago de cliente directamente a cuenta bancaria de liqueed por el total de una factura
Dado que "Kiosquito" es cliente
Cuando se facture desde liqueed "500" pesos el "03/01/2010" al cliente "Kiosquito" con "0" pesos de gastos
Y el cliente "Kiosquito" pague la ultima factura por transferencia bancaria el "04/01/2010"
Entonces el cliente "Kiosquito" adeuda "0" pesos

Escenario: Pago de cliente directamente a cuenta bancaria de consultor por el total de una factura
Dado que "Kiosquito" es cliente
Cuando "Alan" facture "500" pesos el "3/1/2010" directamente al cliente "Kiosquito" con "0" pesos de gastos
Y el cliente "Kiosquito" pague la ultima factura por transferencia bancaria el "04/01/2010"
Entonces el cliente "Kiosquito" adeuda "0" pesos

Escenario: Se cobra via liqueed un trabajo hecho por muchos consultores
Dado que "OSDE" es cliente
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "OSDE" con "0" pesos de gastos
    Y el mentoring lo hizo "David" con un peso del "25%" sobre el total facturado
    Y el reparto fue 
        | Consultor | %  |
        | David     | 50 |
        | Vani      | 30 |
        | Mariano   | 20 |        
    Y el cliente "OSDE" pague la ultima factura por transferencia bancaria el "04/01/2010"
Entonces el saldo disponible del fondo administrativo es de "100" pesos
    Y el saldo disponible del fondo líquido es de "50" pesos
    Y el saldo bruto disponible de cobro de "David" con liqueed es de "550"
    Y el saldo bruto disponible de cobro de "Vani" con liqueed es de "180"
    Y el saldo bruto disponible de cobro de "Mariano" con liqueed es de "120"

Escenario: Se cobra via liqueed un trabajo hecho por un consultor
Dado que "BIND" es cliente
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "BIND" con "0" pesos de gastos
    Y el único consultor sea "David"        
    Y el cliente "BIND" pague la ultima factura por transferencia bancaria el "04/01/2010"
Entonces el saldo disponible del fondo administrativo es de "100" pesos
    Y el saldo disponible del fondo líquido es de "50" pesos
    Y el saldo bruto disponible de cobro de "David" con liqueed es de "850"
