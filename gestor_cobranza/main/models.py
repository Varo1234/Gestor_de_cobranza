from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cobranza(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_captura = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=200)
    domicilio = models.CharField(max_length=200)
    zona = models.CharField(max_length=100)
    saldo_credito = models.DecimalField(max_digits=10, decimal_places=2)
    abono_semanal = models.DecimalField(max_digits=10, decimal_places=2)
    cobrador = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    semanas_atrasado = models.IntegerField()
    saldo_vencido = models.DecimalField(max_digits=10, decimal_places=2)
    pago_minimo = models.DecimalField(max_digits=10, decimal_places=2)


class Pago(models.Model):
    cobranza = models.ForeignKey(Cobranza, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos')
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)