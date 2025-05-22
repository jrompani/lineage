from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import *
from core.admin import BaseModelAdmin, BaseModelAdminAbstratic
from .forms import DashboardContentForm, DashboardContentTranslationForm, CustomUserChangeForm, CustomUserCreationForm


@admin.register(User)
class UserAdmin(BaseModelAdmin, DefaultUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = (
        'username', 'email', 'display_groups', 'cpf', 'gender', 'fichas',
        'is_email_verified', 'is_2fa_enabled', 'created_at', 'updated_at'
    )
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'uuid')
    
    fieldsets = (
        (None, {'fields': ('username', 'password', 'uuid')}),
        ('Informações pessoais', {
            'fields': ('email', 'avatar', 'bio', 'cpf', 'gender')
        }),
        ('Verificação e segurança', {
            'fields': ('is_email_verified', 'is_2fa_enabled')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Datas importantes', {
            'fields': ('last_login', 'created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'avatar', 'bio', 'cpf', 'gender',
                'is_verified', 'is_2fa_enabled'
            ),
        }),
    )

    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    display_groups.short_description = "Grupos"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        js = ('js/mask-cpf.js',)


@admin.register(AddressUser)
class AddressAdmin(BaseModelAdmin):
    list_display = ('user', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code')
    search_fields = ('user__username', 'street', 'city', 'state', 'postal_code', 'neighborhood')
    list_filter = ('state', 'neighborhood')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
    

@admin.register(State)
class StateAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'abbreviation')  # Campos a serem exibidos na lista
    search_fields = ('name', 'abbreviation')  # Campos que podem ser pesquisados
    ordering = ('name',)  # Ordenação padrão
    list_filter = ('abbreviation',)  # Filtro para a lista


@admin.register(City)
class CityAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'state')  # Campos a serem exibidos na lista
    search_fields = ('name',)  # Campos que podem ser pesquisados
    ordering = ('name',)  # Ordenação padrão
    list_filter = ('state',)  # Filtro para a lista


class DashboardContentTranslationInline(admin.TabularInline):
    model = DashboardContentTranslation
    form = DashboardContentTranslationForm
    extra = 1
    fields = ['language', 'title', 'content']


@admin.register(DashboardContent)
class DashboardContentAdmin(BaseModelAdmin):
    form = DashboardContentForm
    inlines = [DashboardContentTranslationInline]

    list_display = ('get_title', 'is_active', 'author')
    list_filter = ('is_active',)
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"Dashboard {obj.pk}"
    get_title.short_description = 'Título (PT)'


@admin.register(SiteLogo)
class SiteLogoAdmin(BaseModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(Conquista)
class ConquistaAdmin(BaseModelAdmin):
    list_display = ('nome', 'codigo', 'descricao')
    search_fields = ('nome', 'codigo')
    list_filter = ('codigo',)
    readonly_fields = ('codigo',)


@admin.register(ConquistaUsuario)
class ConquistaUsuarioAdmin(BaseModelAdmin):
    list_display = ('usuario', 'conquista', 'data_conquista')
    search_fields = ('usuario__username', 'conquista__nome')
    list_filter = ('conquista', 'data_conquista')


@admin.register(PerfilGamer)
class PerfilGamerAdmin(BaseModelAdmin):
    list_display = ('user', 'level', 'xp', 'last_login_reward')
    search_fields = ('user__username',)
    list_filter = ('level', 'last_login_reward')
    readonly_fields = ('xp', 'level', 'last_login_reward')
