from django import forms
from .models import Solicitation


class SolicitationForm(forms.ModelForm):
    class Meta:
        model = Solicitation
        fields = []  # Nenhum campo visível, o usuário será atribuído automaticamente


class EventForm(forms.Form):
    action = forms.CharField(max_length=255, label="Descrição do Evento")
    image = forms.ImageField(required=False, label="Imagem (opcional)")
