from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Cobranza, Pago, UploadFile
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .forms import UploadFileForm
import pandas as pd
import os


def is_admin(user):
    return user.is_staff  # Puedes ajustar esto para que se adapte a tus necesidades


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña inválidos.')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    return render(request, 'home.html')


@login_required
def subpage_view(request):
    return render(request, 'subpage.html')


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
        elif check_password(old_password, request.user.password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'La contraseña ha sido cambiada con éxito.')
            return redirect('home')
        else:
            messages.error(request, 'La antigua contraseña es incorrecta.')
    return render(request, 'change_password.html')


@login_required
def cobranza_view(request):
    if request.user.is_staff:
        cobranzas = Cobranza.objects.all()
    else:
        cobranzas = Cobranza.objects.filter(usuario=request.user)
    return render(request, 'cobranza.html', {'cobranzas': cobranzas})


@login_required
def deudor_detail(request, id):
    cobranza = get_object_or_404(Cobranza, id=id)  # Usa Cobranza en lugar de Deudor
    return render(request, 'deudor.html', {'cobranza': cobranza})


@login_required
def agregar_pago(request, id):
    cobranza = get_object_or_404(Cobranza, id=id)
    pagos = Pago.objects.filter(cobranza=cobranza)

    if request.method == 'POST':
        monto = request.POST.get('monto')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')

        Pago.objects.create(
            cobranza=cobranza,
            usuario=request.user,
            monto=monto,
            latitud=latitud,
            longitud=longitud,
        )

        return redirect('deudor_detail', id=id)

    return render(request, 'agregar_pago.html', {'cobranza': cobranza, 'pagos': pagos})


@login_required
@user_passes_test(is_admin)
def subpage_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            file_extension = os.path.splitext(instance.file.name)[1]
            if file_extension not in ['.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt']:
                messages.error(request, "El archivo subido no es un archivo Excel. Por favor, sube un archivo Excel.")
                return redirect('subpage')

            instance.save()

            # After saving, you can process the file
            df = pd.read_excel(instance.file.path)

            for cobrador in df['cobrador'].unique():
                if not User.objects.filter(username=cobrador).exists():
                    messages.error(request,
                                   f"El usuario {cobrador} no existe en el sistema. Por favor, registra este usuario antes de continuar.")
                    instance.delete()  # Delete the file
                    return redirect('subpage')

            # Here you can process the dataframe as you need, for example:
            for index, row in df.iterrows():
                Cobranza.objects.create(
                    usuario=User.objects.get(username=row['cobrador']),
                    fecha_captura=pd.to_datetime(row['fecha_captura']).date(),
                    nombre=row['nombre'],
                    domicilio=row['domicilio'],
                    zona=row['zona'],
                    saldo_credito=row['saldo_credito'],
                    abono_semanal=row['abono_semanal'],
                    cobrador=row['cobrador'],
                    monto=row['monto'],
                    semanas_atrasado=row['semanas_atrasado'],
                    saldo_vencido=row['saldo_vencido'],
                    pago_minimo=row['pago_minimo'],
                )

            return redirect('subpage')
    else:
        form = UploadFileForm()
    files = UploadFile.objects.all()  # Assuming your model has a 'user' field
    return render(request, 'subpage.html', {'form': form, 'files': files})