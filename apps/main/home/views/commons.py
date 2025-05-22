import logging

from ..models import *
from ..forms import *

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.translation import activate

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login

from utils.render_theme_page import render_theme_page
from utils.services import verificar_conquistas
from utils.dynamic_import import get_query_class

LineageStats = get_query_class("LineageStats")
logger = logging.getLogger(__name__)


def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)


def empty_view(request):
    return HttpResponse(status=404)


def terms_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'terms.html', context)


def user_agreement_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'user_agreement.html', context)


def privacy_policy_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'privacy_policy.html', context)


def verificar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])

            # Adiciona XP
            perfil = PerfilGamer.objects.get(user=user)
            perfil.adicionar_xp(40)  # valor de XP por verificar e-mail

            # Verifica conquistas
            conquistas_desbloqueadas = verificar_conquistas(user, request=request)

            # Opcional: Armazena mensagem para exibir no template
            context = {
                'sucesso': True,
                'conquistas': conquistas_desbloqueadas,
                'xp': 40,
            }
        else:
            # Já verificado anteriormente
            context = {'ja_verificado': True}
    else:
        context = {'erro': True}

    return render_theme_page(request, 'public', 'email_verificado.html', context)


def custom_set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')

        if lang_code:
            response = HttpResponseRedirect(next_url)
            response.set_cookie('django_language', lang_code)
            activate(lang_code)

            # Verifica se o usuário já trocou de idioma antes
            if request.user.is_authenticated:
                perfil = PerfilGamer.objects.get(user=request.user)
                
                # Usa uma conquista para marcar se já fez isso antes
                if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='idioma_trocado').exists():
                    perfil.adicionar_xp(20)  # XP por trocar idioma
                    conquistas = verificar_conquistas(request.user, request=request)
                    for conquista in conquistas:
                        messages.success(request, f"🏆 Conquista desbloqueada: {conquista.nome}")
                    messages.success(request, "Idioma alterado com sucesso! Você ganhou 20 XP.")

            return response

    return redirect('/')


def registration_success_view(request):
    return render(request, 'accounts_custom/registration_success.html')


def verify_2fa_view(request):
    if request.method == 'POST':
        user_id = request.session.get('pre_2fa_user_id')
        if not user_id:
            return redirect('login')

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        token = request.POST.get('token')
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if device:
            if device.verify_token(token):
                request.user = user  # necessário para otp_login
                otp_login(request, device)  # <- isto marca o 2FA como verificado
                login(request, user)        # autentica o usuário na sessão Django
                del request.session['pre_2fa_user_id']
                return redirect('dashboard')
            else:
                return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Código inválido.', 'user': request.user})
        else:
            return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Dispositivo 2FA não configurado ou não confirmado.', 'user': request.user})
    
    return render(request, 'accounts_custom/verify-2fa.html', {'user': request.user})
