from django.contrib import admin
from core.admin import BaseModelAdmin
from .models import *


@admin.register(Solicitation)
class SolicitationAdmin(BaseModelAdmin):
    list_display = ('protocol', 'status')
    search_fields = ('protocol',)
    list_filter = ('status',)
    ordering = ('-created_at',)


@admin.register(SolicitationHistory)
class SolicitationHistoryAdmin(admin.ModelAdmin):
    list_display = ('solicitation', 'action', 'timestamp', 'user')
    search_fields = ('solicitation__protocol', 'action', 'user__username')
    list_filter = ('timestamp', 'user') 


@admin.register(SolicitationParticipant)
class SolicitationParticipantAdmin(BaseModelAdmin):
    list_display = ('user', 'solicitation', 'solicitation_protocol', 'user_email')
    search_fields = ('user__username', 'solicitation__protocol')
    list_filter = ('solicitation__protocol',)

    def solicitation_protocol(self, obj):
        return obj.solicitation.protocol
    solicitation_protocol.short_description = 'Protocolo da Solicitação'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email do Usuário'
