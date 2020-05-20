#language:es
Característica: Importación de archivo .CSV de movimientos de la cuenta en pesos del Banco Santander

Escenario: Importación de archivo mínimo (solo 2 registros: 1 del día y 1 reciente)
Cuando se importa el archivo de movimientos "test-data/movimientos-minimos.csv"
Entonces existe el movimiento del "07/08/2019" con sucursal de origen código "0000" y descripción "Casa Central", código operativo "4719", referencia "065898243", concepto "Pago Electronico De Servicios  - Imp.afip: 3071528100327225574", importe "-142994,20" y saldo "0,00"
Y existe el movimiento del "06/08/2019" con sucursal de origen código "0762" y descripción "Cerrito", código operativo "4633", referencia "000002292", concepto "Imp Ley 25413 Deb 0,6%", importe "-1452,49" y saldo "791997,54"