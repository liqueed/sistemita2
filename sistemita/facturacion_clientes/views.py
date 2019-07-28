from django.shortcuts import render

def subir_resumen_bancario(request):
    return render(request, 'facturacion_clientes/subir_resumen_bancario.html', {})