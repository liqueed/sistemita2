from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from core.forms import MedioPagoForm
from core.models.mediopago import MedioPago
from core.serializers import MedioPagoSerializer


class MedioPagoViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    queryset = MedioPago.objects.all()
    serializer_class = MedioPagoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MedioPagoListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        # Search filter
        queryset = MedioPago.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                nombre__icontains=search
            )
        return queryset


class MedioPagoAgregarView(LoginRequiredMixin, CreateView):
    model = MedioPago
    form_class = MedioPagoForm
    success_url = reverse_lazy('mediopago-listado')


class MedioPagoDetalleView(LoginRequiredMixin, DetailView):
    queryset = MedioPago.objects.all()


class MedioPagoModificarView(LoginRequiredMixin, UpdateView):
    queryset = MedioPago.objects.all()
    form_class = MedioPagoForm
    success_url = reverse_lazy('mediopago-listado')


class MedioPagoEliminarView(LoginRequiredMixin, DeleteView):
    queryset = MedioPago.objects.all()
    success_url = reverse_lazy('mediopago-listado')
