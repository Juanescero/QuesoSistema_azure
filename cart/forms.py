from django import forms
from users.models import CustomUser

class ClienteProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['imagen', 'email', 'documento', 'segundo_nombre', 'segundo_apellido', 'telefono']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }