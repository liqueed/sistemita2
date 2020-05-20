#language: es
Característica: Deuda de los clientes con liqueed (una vez facturado)

Escenario: Simple facturación y deuda posterior
Dado que "Kiosquito" es cliente
Cuando se facture desde liqueed hoy "500" pesos a "Kiosquito" sin gastos
Entonces el cliente "Kiosquito" adeuda "500" pesos

Escenario: Tiempo faltante para cobro según demora prometida de pago
Dado que "Kiosquito" es cliente
    Y que el cliente "Kiosquito" demora los pagos "30" días
Cuando se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "Kiosquito" con "0" pesos de gastos
Entonces el "12/1/2010" faltarán "20" días para que "Kiosquito" pague la última factura

Escenario: Un consultor factura directamente al cliente
Dado que "Kiosquito" es cliente
Y que "Barcito" es cliente
Cuando "Alan" facture "500" pesos el "3/1/2010" directamente al cliente "Kiosquito" con "0" pesos de gastos
Y "Alan" facture "500" pesos el "4/1/2010" directamente al cliente "Barcito" con "0" pesos de gastos
Y se facture desde liqueed "1000" pesos el "2/1/2010" al cliente "Kiosquito" con "0" pesos de gastos
Entonces el cliente "Kiosquito" adeuda "1500" pesos
Y el cliente "Barcito" adeuda "500" pesos
Y hay "500" pesos pendientes de pago de "Kiosquito" directamente a "Alan"
Y hay "1000" pesos pendientes de pago de "Kiosquito" a liqueed