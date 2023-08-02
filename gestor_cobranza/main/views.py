from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from .models import Cobranza, Pago
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Return an 'invalid login' error message.
            ...
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


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def cobranza_view(request):
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