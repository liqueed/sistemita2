from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import FormSubirArchivoMovimientosBancarios
from .lector_archivo_de_movimientos_bancarios import LectorArchivoDeMovimientosBancarios

def subir_resumen_bancario(request):
    if request.method == 'POST':
        form = FormSubirArchivoMovimientosBancarios(request.POST, request.FILES)
        if form.is_valid():
            LectorArchivoDeMovimientosBancarios.importar_archivo_subido_en_memoria(request.FILES['archivo_de_movimientos_bancarios'])
            return HttpResponseRedirect('/conciliar_movimientos_bancarios/')
    else:
        form = FormSubirArchivoMovimientosBancarios()
        return render(request, 'facturacion_clientes/subir_resumen_bancario.html', {'form' : form})

def importar_resumen_bancario():
    pass
        
