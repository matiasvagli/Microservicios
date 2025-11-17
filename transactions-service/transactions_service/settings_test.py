"""Configuración de Django para ejecutar tests localmente con sqlite.
Este archivo importa la configuración principal y sobrescribe DATABASES para usar sqlite3,
evitando la dependencia de PostgreSQL en entornos locales de CI o máquina dev.
"""
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Evitar enviar correo real durante tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
