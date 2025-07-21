from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu usuário',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite sua senha',
            'class': 'form-control',
        })
    ) 