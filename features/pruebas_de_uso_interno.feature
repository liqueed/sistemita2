#language:es
Característica: A la hora de conciliar movimientos automáticamente es necesario chequear si un CBU es de un socio o no

Escenario: Dos consultores, uno con 1 CBU y otro con 2, se chequean un CBU existente y uno inexistente
Dado que el consultor "David" tiene la siguiente estrategia tributaria
    | CUIT        | CBU                    |
    | 24270501601 | 1500035000008161431046 |
    | 27272255747 | 2070066530004021386186 |
Y que el consultor "Alan" tiene la siguiente estrategia tributaria
    | CUIT        | CBU                    |
    | 27270501682 | 1600035000008161431048 |
Entonces el cbu "1500035000008161431046" es de algún consultor
Y el cbu "1500035000008161431987" no es de ningún consultor