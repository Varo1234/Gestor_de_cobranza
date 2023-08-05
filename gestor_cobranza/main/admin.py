from django.contrib import admin
from .models import Cobranza, UploadFile, Pago, RegistroHoras

admin.site.register(Cobranza)
admin.site.register(Pago)
admin.site.register(UploadFile)
admin.site.register(RegistroHoras)
