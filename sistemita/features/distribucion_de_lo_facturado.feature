#language: es
Característica: Distribución de lo facturado a un cliente en distintos conceptos

Escenario: 
Dado que "OSDE" es cliente
Cuando se facture "1000" pesos el "2/1/2010" al cliente "OSDE" con "0" pesos de gastos
    Y el mentoring lo hizo "David" con un peso del "25%" sobre el total facturado
    Y el reparto fue 
        | Consultor | %  |
        | David     | 50 |
        | Vani      | 30 |
        | Mariano   | 20 |        
Entonces el saldo pendiente de cobro del fondo administrativo es de "100" pesos
    Y el saldo pendiente de cobro del fondo líquido es de "50" pesos
    Y el saldo pendiente de cobro de "David" con liqueed es de "550"
    Y el saldo pendiente de cobro de "Vani" con liqueed es de "180"
    Y el saldo pendiente de cobro de "Mariano" con liqueed es de "120"