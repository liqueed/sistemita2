import os
import os.path
import csv
from datetime import datetime 
from decimal import Decimal
import locale
from .models import MovimientoBancario

class LectorArchivoDeMovimientosBancarios:
    
        
    @staticmethod
    def importar_nombre_archivo(nombre_archivo):
        path_completo_al_archivo = os.path.join(os.getcwd(), nombre_archivo)
        with open(path_completo_al_archivo, 'r', encoding='ISO-8859-1') as archivo:
           movimientos = LectorArchivoDeMovimientosBancarios.importar_movimientos(archivo)
           MovimientoBancario.objects.bulk_create(movimientos)
            

    @staticmethod
    def importar_movimientos(archivo):
        movimientos = []
        locale.setlocale(locale.LC_ALL,'es_AR.iso88591')
        for linea in archivo:
            elementos_de_la_lista = linea.split('\t')
            if len(elementos_de_la_lista)>1 and elementos_de_la_lista[0][0]!='F':
                elementos_de_la_lista[0] = datetime.strptime(elementos_de_la_lista[0], '%d/%m/%Y')
                elementos_de_la_lista[5] = elementos_de_la_lista[5].strip()
                elementos_de_la_lista[6] = locale.atof(elementos_de_la_lista[6].translate(str.maketrans('()','- ')), Decimal)
                elementos_de_la_lista[7] = locale.atof(elementos_de_la_lista[7].translate(str.maketrans('()','- ')), Decimal)
                movimientos.append(MovimientoBancario(fecha=elementos_de_la_lista[0],
                    codigo_sucursal=elementos_de_la_lista[1],
                    descripcion_sucursal=elementos_de_la_lista[2],
                    codigo_operativo=elementos_de_la_lista[3],
                    referencia=elementos_de_la_lista[4],
                    concepto=elementos_de_la_lista[5],
                    importe_pesos=elementos_de_la_lista[6],
                    saldo_pesos=elementos_de_la_lista[7]))
        return movimientos
                