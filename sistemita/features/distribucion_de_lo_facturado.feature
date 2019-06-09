#language: es
Característica: Distribución de lo facturado a un cliente en distintos conceptos

Escenario: 
Dado que "OSDE" es cliente
    Y que la distribución por default es del "10%" para fondo administrativo, "5%" para el fondo líquido, "20%" para mentoring y "65%" para el delivery
Cuando se facture "1000" pesos el "2/1/2010" al cliente "OSDE" con "0" pesos de gastos
    Y el mentoring lo hizo "David"
    Y el reparto fue 
        | Persona | %  |
        | David   | 50 |
        | Vani    | 30 |
        | Mariano | 20 |        
Entonces el saldo del fondo administrativo es de "100" pesos
    Y el saldo del fondo líquido es de "50" pesos
    Y el saldo de "David" con liqueed es de "525"
    Y el saldo de "Vani" con liqueed es de "195"
    Y el saldo de "Mariano" con liqueed es de "130"