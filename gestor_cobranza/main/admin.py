from django.contrib import admin
from .models import Cobranza, UploadFile, Pago  # Importa todos los modelos que quieras añadir

admin.site.register(Cobranza)
admin.site.register(Pago)
admin.site.register(UploadFile)