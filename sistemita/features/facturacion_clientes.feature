#language:es
Característica: Confección de facturas

Escenario: Se recuerda la última factura confeccionada para que los escenarios no sean tan verborrágicos
Dado que "Kiosquito" es cliente
Cuando se facture "500" pesos el "3/1/2010" al cliente "Kiosquito" con "100" pesos de gastos
Entonces la última factura fue de "500" pesos realizada el "3/1/2010" al cliente "Kiosquito" con "100" pesos de gastos