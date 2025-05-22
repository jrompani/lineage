from django.contrib import admin
from .models import News, NewsTranslation
from core.admin import BaseModelAdmin
from .forms import NewsForm, NewsTranslationForm
from django import forms


class NewsTranslationInline(admin.TabularInline):
    model = NewsTranslation
    form = NewsTranslationForm
    extra = 1
    fields = ['language', 'title', 'content', 'summary']
    formset = forms.BaseInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(NewsTranslationInline, self).get_formset(request, obj, **kwargs)
        # Aqui você pode personalizar o formset para exibir apenas as traduções necessárias
        return formset


@admin.register(News)
class NewsAdmin(BaseModelAdmin):
    form = NewsForm
    inlines = [NewsTranslationInline]

    list_display = ('get_title', 'author', 'pub_date', 'is_published', 'is_private')
    list_filter = ('is_published', 'is_private')
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user

        super().save_model(request, obj, form, change)

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"News {obj.pk}"
    get_title.short_description = 'Título (PT)'
