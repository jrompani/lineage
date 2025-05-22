from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from apps.main.home.decorator import conditional_otp_required
from django.utils.translation import gettext as _

from apps.main.notification.models import Notification
from apps.main.news.models import News
from apps.main.solicitation.models import Solicitation, SolicitationParticipant
from django.http import HttpResponse, Http404
from django.conf import settings
import os
from core.context_processors import active_theme
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import *


@staff_member_required
def get_latest_news(request):
    news = News.objects.filter(is_published=True).order_by('-pub_date')[:5]
    data = list(news.values('title', 'slug', 'content', 'pub_date'))
    return JsonResponse(data, safe=False)


@staff_member_required
def get_latest_notifications(request):
    notifications = Notification.objects.order_by('-created_at')[:5]
    data = list(notifications.values('notification_type', 'message'))
    return JsonResponse(data, safe=False)


@conditional_otp_required
def chat_room(request, group_name):
    solicitation = None
    type_chat = None

    try:
        solicitation = Solicitation.objects.get(protocol=group_name)
        # Verifica se o usuário é participante
        is_participant = SolicitationParticipant.objects.filter(
            solicitation=solicitation, user=request.user
        ).exists()
        type_chat = "Solicitação"
        
        # Se for um staff, automaticamente adiciona como participante, se não for
        if request.user.is_staff and not is_participant:
            SolicitationParticipant.objects.create(solicitation=solicitation, user=request.user)
            is_participant = True  # Marca como participante
    except Solicitation.DoesNotExist:
        raise Http404(f"Protocolo {group_name} não encontrado.")

    # Verifica se o usuário é participante
    if not is_participant:
        raise Http404(_("Você não tem permissão para acessar esta sala de chat."))

    # Verifica se o status é 'pending'
    if solicitation.status != 'pending':
        return render(request, 'errors/solicitation_closed.html', {
            'solicitation': solicitation,
            'status': solicitation.get_status_display(),  # Exibe 'Aprovado', 'Rejeitado', etc
        })

    if request.user.avatar:
        custom_imagem = '/decrypted-file/home/user/avatar/'
        avatar_url = custom_imagem + str(request.user.uuid) + '/'
    else:
        avatar_url = '/static/assets/img/team/generic_user.png'

    solicitation_name = (
        str(solicitation.user.username).upper() + ' - ' + str(solicitation.user.email)
        if solicitation.user else "Solicitação sem usuário..."
    )

    chat_messages = ChatGroup.objects.filter(group_name=group_name).order_by('timestamp')
    solicitation_context = 'do Usuário:'

    return render(request, 'pages/group.html', {
        'group_name': group_name,
        'avatar_url': avatar_url,
        'username': request.user.username,
        'chat_messages': chat_messages,
        'solicitation': solicitation_name,
        'solicitation_context': solicitation_context,
        'type_chat': type_chat,
    })


@conditional_otp_required
def error_chat(request):
    return render(request, 'errors/access_denied.html', {
        'message': 'Você não tem permissão para acessar esta sala de chat.'
    })


def serve_theme_file(request, file_name):
    # Obtém o contexto do tema ativo
    context_data = active_theme(request)
    path_theme = context_data.get('path_theme')

    if not path_theme:
        raise Http404(_("Tema não encontrado."))

    # Caminho relativo com separador compatível com Django
    template_relative_path = os.path.join(path_theme, file_name + '.html').replace('\\', '/').replace("/themes/", "")

    # Verifica se o arquivo existe no sistema de arquivos
    if not os.path.isfile(os.path.join(settings.BASE_DIR, path_theme.replace("/themes/", "themes/"), file_name + '.html')):
        raise Http404(_("Arquivo não encontrado no tema."))

    # Renderiza o template
    return render(request, template_relative_path)


@conditional_otp_required
def security_settings(request):
    user = request.user

    # Verifica se há um dispositivo 2FA confirmado
    has_2fa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()

    return render(request, 'security/settings.html', {
        'two_factor_enabled': has_2fa,
    })
