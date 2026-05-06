from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente
 
class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True, label='Nombre'
    )
    email = forms.EmailField(
        required=True, label='Correo electrónico'
    )
    direccion = forms.CharField(
        max_length=250, required=False, label='Dirección'
    )
 
    class Meta:
        model  = Cliente
        fields = ['first_name', 'last_name', 'username', 'email', 'direccion', 'password1', 'password2']
 
 
