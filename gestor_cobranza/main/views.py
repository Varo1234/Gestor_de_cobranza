import os
import pandas as pd
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils import timezone

from .models import Cobranza, Pago, UploadFile, RegistroHoras
from .forms import UploadFileForm


def is_admin(user):
    return user.is_staff  # Puedes ajustar esto para que se adapte a tus necesidades


def login_view(request):
    """
        Esta vista maneja el inicio de sesión del usuario. Autentica al usuario y,
        si la autenticación es exitosa, redirige al usuario a la página de inicio.
        """
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
    """
        Esta vista maneja el cierre de sesión del usuario. Cierra la sesión y
        redirige al usuario a la página de inicio de sesión.
        """
    logout(request)
    return redirect('login')


def home_view(request):
    """
        Esta vista muestra la página de inicio.
        """
    return render(request, 'home.html')


def change_password(request):
    """
        Esta vista maneja el cambio de contraseña del usuario. Comprueba si la
        contraseña antigua es correcta y si las nuevas contraseñas coinciden, y
        luego cambia la contraseña.
        """
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
    """
        Esta vista muestra las cobranzas. Si el usuario es un administrador,
        muestra todas las cobranzas. Si no, muestra solo las cobranzas del usuario actual.
        """
    if request.user.is_staff:
        cobranzas = Cobranza.objects.all()
    else:
        cobranzas = Cobranza.objects.filter(usuario=request.user)
    return render(request, 'cobranza.html', {'cobranzas': cobranzas})


@login_required
def deudor_detail(request, id):
    """
        Esta vista muestra los detalles de una cobranza específica.
        """
    cobranza = get_object_or_404(Cobranza, id=id)  # Usa Cobranza en lugar de Deudor
    if request.user != cobranza.usuario and not request.user.is_staff:
        return redirect('home')  # O redirige a donde quieras si el usuario no tiene permiso para ver esta cobranza
    return render(request, 'deudor.html', {'cobranza': cobranza})


@login_required
def agregar_pago(request, id):
    """
        Esta vista maneja la adición de pagos a una cobranza específica.
        """
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

        # return redirect('deudor_detail', id=id)

    return render(request, 'agregar_pago.html', {'cobranza': cobranza, 'pagos': pagos})


@login_required
@user_passes_test(is_admin)
def archivos_view(request):
    """
        Esta vista maneja la subida de archivos y la creación de cobranzas a
        partir de los datos en el archivo subido. Solo los usuarios administradores
        pueden subir archivos.
        """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            file_extension = os.path.splitext(instance.file.name)[1]
            if file_extension not in ['.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt']:
                messages.error(request, "El archivo subido no es un archivo Excel. Por favor, sube un archivo Excel.")
                return redirect('archivos')

            instance.save()

            # After saving, you can process the file
            df = pd.read_excel(instance.file.path)

            for cobrador in df['cobrador'].unique():
                if not User.objects.filter(username=cobrador).exists():
                    messages.error(request,
                                   f"El usuario {cobrador} no existe en el sistema. Por favor, registra este usuario antes de continuar.")
                    instance.delete()  # Delete the file
                    return redirect('archivos')

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

            return redirect('archivos')
    else:
        form = UploadFileForm()
    files = UploadFile.objects.all()  # busca todos los archivos
    return render(request, 'archivos.html', {'form': form, 'files': files})


@login_required
def registro_horas_view(request):
    """
        Esta vista maneja el registro de horas de entrada del usuario. El usuario
        puede registrar su hora de entrada una vez al día. La vista muestra todos
        los registros de horas de entrada del usuario.
        """
    hoy = timezone.now().date()
    ya_registrado = RegistroHoras.objects.filter(usuario=request.user, hora_entrada__date=hoy).exists()
    if request.method == 'POST' and not ya_registrado:
        RegistroHoras.objects.create(usuario=request.user, hora_entrada=timezone.now())
    registros = RegistroHoras.objects.filter(usuario=request.user).order_by('-hora_entrada')
    return render(request, 'registro_horas.html', {'registros': registros, 'ya_registrado': ya_registrado})