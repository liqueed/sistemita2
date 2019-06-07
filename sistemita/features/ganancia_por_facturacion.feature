#language: es
Característica: Cálculo de ganancia por trabajo realizado

Escenario: Ganancia es monto facturado menos gastos
Dado que "Kiosquito" es cliente
Cuando se facture "500" pesos el "2/1/2010" al cliente "Kiosquito" con "100" pesos de gastos
Entonces la ganancia obtenida por el trabajo hecho a "Kiosquito" será de "400" pesos

Escenario: Ganancia mensual total es la suma de la ganancia de todas las facturas de un mensual
Dado que "Kiosquito" es cliente
Cuando se facture "500" pesos el "3/1/2010" al cliente "Kiosquito" con "100" pesos de gastos
Y se facture "100" pesos el "2/1/2010" al cliente "Kiosquito" con "10" pesos de gastos
Entonces la ganancia total obtenida por liqueed al día de hoy es de "490" pesos