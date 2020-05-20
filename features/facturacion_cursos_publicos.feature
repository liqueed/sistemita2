#language: es
Característica: Un curso público requiere múltiples facturas

Escenario: Un individuo (consumidor final) se anota en un curso público
Dado que está publicado un "CSM" el "01/06/2010" dictado por "Alan"
Cuando se inscriba "Juan Perez" en el "CSM" del "01/06/2010" con un costo de "1000" pesos
Y se haya facturado el "01/05/2010" la inscripción de "Juan Perez" en el "CSM" del "01/06/2010"
Entonces el cliente "Juan Perez" adeuda "1000" pesos

Escenario: Un cliente inscribe varias personas en un curso público
Dado que está publicado un "CSM" el "01/06/2010" dictado por "Alan"
Y que "Kiosquito" es cliente
Cuando se el cliente "Kiosquito" inscriba "3" personas en el "CSM" del "01/06/2010" con un costo de "1000" pesos cada una
Y se haya facturado la inscripción de los participantes de "Kiosquito" en el "CSM" del "01/06/2010"
Entonces el cliente "Kiosquito" adeuda "3000" pesos

Escenario: Cálculo de monto adeudado en un curso con inscriptos individuales y en grupo
Dado que está publicado un "CSM" el "01/06/2010" dictado por "Alan"
Y que "Kiosquito" es cliente
Cuando se inscriba "Juan Perez" en el "CSM" del "01/06/2010" con un costo de "1000" pesos
Y se haya facturado el "01/05/2010" la inscripción de "Juan Perez" en el "CSM" del "01/06/2010"
Y se el cliente "Kiosquito" inscriba "3" personas en el "CSM" del "01/06/2010" con un costo de "1000" pesos cada una
Y se haya facturado la inscripción de los participantes de "Kiosquito" en el "CSM" del "01/06/2010"
Entonces la deuda total de clientes para el "CSM" del "01/06/2010" es de "4000" pesos