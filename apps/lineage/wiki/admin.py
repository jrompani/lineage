from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    WikiPage, WikiPageTranslation,
    WikiSection, WikiSectionTranslation,
    WikiUpdate, WikiUpdateTranslation,
    WikiEvent, WikiEventTranslation,
    WikiRate, WikiRateTranslation,
    WikiFeature, WikiFeatureTranslation
)
from core.admin import BaseModelAdmin


class WikiPageTranslationInline(admin.StackedInline):
    model = WikiPageTranslation
    extra = 1
    min_num = 1


@admin.register(WikiPage)
class WikiPageAdmin(BaseModelAdmin):
    list_display = ('get_title', 'slug', 'order', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('translations__title', 'translations__content')
    ordering = ('order', 'id')
    inlines = [WikiPageTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiSectionTranslationInline(admin.StackedInline):
    model = WikiSectionTranslation
    extra = 1
    min_num = 1


@admin.register(WikiSection)
class WikiSectionAdmin(BaseModelAdmin):
    list_display = ('get_title', 'page', 'section_type', 'order', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'page', 'section_type', 'created_at', 'updated_at')
    search_fields = ('translations__title', 'translations__content', 'translations__subtitle', 'translations__description')
    ordering = ('page', 'order', 'id')
    inlines = [WikiSectionTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiUpdateTranslationInline(admin.StackedInline):
    model = WikiUpdateTranslation
    extra = 1
    min_num = 1


@admin.register(WikiUpdate)
class WikiUpdateAdmin(BaseModelAdmin):
    list_display = ('version', 'release_date', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'release_date', 'created_at', 'updated_at')
    search_fields = ('version', 'translations__content')
    ordering = ('-release_date', '-version')
    inlines = [WikiUpdateTranslationInline]


class WikiEventTranslationInline(admin.StackedInline):
    model = WikiEventTranslation
    extra = 1
    min_num = 1


@admin.register(WikiEvent)
class WikiEventAdmin(BaseModelAdmin):
    list_display = ('get_title', 'event_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'event_type', 'created_at', 'updated_at')
    search_fields = (
        'translations__title',
        'translations__description',
        'translations__requirements',
        'translations__rewards'
    )
    ordering = ('event_type', 'id')
    inlines = [WikiEventTranslationInline]

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else '-'
    get_title.short_description = _('Title')


class WikiRateTranslationInline(admin.StackedInline):
    model = WikiRateTranslation
    extra = 1


@admin.register(WikiRate)
class WikiRateAdmin(BaseModelAdmin):
    list_display = ('rate_type', 'value', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'rate_type')
    search_fields = ('rate_type', 'translations__title', 'translations__content')
    ordering = ('rate_type', '-created_at')
    inlines = [WikiRateTranslationInline]


class WikiFeatureTranslationInline(admin.StackedInline):
    model = WikiFeatureTranslation
    extra = 1


@admin.register(WikiFeature)
class WikiFeatureAdmin(BaseModelAdmin):
    list_display = ('feature_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'feature_type')
    search_fields = ('feature_type', 'translations__title', 'translations__content')
    ordering = ('feature_type', '-created_at')
    inlines = [WikiFeatureTranslationInline]
