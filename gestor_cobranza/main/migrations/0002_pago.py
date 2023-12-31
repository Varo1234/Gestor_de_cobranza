# Generated by Django 4.2.3 on 2023-07-31 21:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('cobranza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='main.cobranza')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
