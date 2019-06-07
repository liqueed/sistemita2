#language: es
Característica: Deuda de los clientes con liqueed (una vez facturado)

Escenario: Simple facturación y deuda posterior
Dado que "Kiosquito" es cliente
Cuando se facture hoy "500" pesos a "Kiosquito" sin gastos
Entonces el cliente "Kiosquito" adeuda "500" pesos

Escenario: Tiempo faltante para cobro según demora prometida de pago
Dado que "Kiosquito" es cliente
    Y que el cliente "Kiosquito" demora los pagos "30" días
Cuando se facture "1000" pesos el "2/1/2010" al cliente "Kiosquito" con "0" pesos de gastos
Entonces el "12/1/2010" faltarán "20" días para que "Kiosquito" pague la última factura