"""
URL configuration for gestor_cobranza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('archivos/', views.archivos_view, name='archivos'),
    path('change_password/', views.change_password, name='change_password'),
    path('cobranza/', views.cobranza_view, name='cobranza'),
    path('deudor/<int:id>/', views.deudor_detail, name='deudor_detail'),
    path('deudor/<int:id>/agregar_pago/', views.agregar_pago, name='agregar_pago'),
    path('registro_horas/', views.registro_horas_view, name='registro_horas'),

]
