from django import forms
from django.contrib import admin
from .models import FAQ, FAQTranslation
from core.admin import BaseModelAdmin


class FAQAdminForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pergunta'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordem'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FAQTranslationInline(admin.TabularInline):
    model = FAQTranslation
    extra = 1
    fields = ('language', 'question', 'answer')
    verbose_name = 'Tradução de FAQ'
    verbose_name_plural = 'Traduções de FAQ'


@admin.register(FAQ)
class FAQAdmin(BaseModelAdmin):
    form = FAQAdminForm
    list_display = ('question', 'order', 'is_public')
    ordering = ('order',)
    list_filter = ('is_public',)
    search_fields = ('question',)
    inlines = [FAQTranslationInline]
