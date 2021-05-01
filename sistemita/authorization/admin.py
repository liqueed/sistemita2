"""Configuraciones del administrador de Admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from sistemita.authorization.models import User

admin.site.register(User, UserAdmin)
