import requests, logging

from ..models import *
from ..forms import *
from ..utils import resolve_templated_path

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth import logout, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils.translation import gettext as _

from utils.notifications import send_notification
from utils.dynamic_import import get_query_class

LineageStats = get_query_class("LineageStats")
logger = logging.getLogger(__name__)


def verificar_hcaptcha(token):
    secret = settings.HCAPTCHA_SECRET_KEY
    data = {
        'response': token,
        'secret': secret,
    }
    r = requests.post('https://hcaptcha.com/siteverify', data=data)
    return r.json().get('success', False)


def logout_view(request):
  logout(request)
  return redirect('/')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        hcaptcha_token = request.POST.get('h-captcha-response')
        hcaptcha_ok = verificar_hcaptcha(hcaptcha_token)

        # Verifica termos + captcha + formulário
        if not request.POST.get('terms'):
            form.add_error(None, 'Você precisa aceitar os termos e condições para se registrar.')

        elif not hcaptcha_ok:
            form.add_error(None, 'Verificação do hCaptcha falhou. Tente novamente.')

        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            try:
                send_mail(
                    subject='Verifique seu e-mail',
                    message=f'Olá {user.username}, clique no link para verificar sua conta: {verification_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Erro ao enviar email: {str(e)}")

            try:
                send_notification(
                    user=None,
                    notification_type='staff',
                    message=f'Usuário {user.username} de email {user.email} cadastrado com sucesso!',
                    created_by=None
                )
            except Exception as e:
                logger.error(f"Erro ao criar notificação: {str(e)}")

            return redirect('registration_success')
        else:
            print(_("Registration failed!"))
    else:
        form = RegistrationForm()

    context = {'form': form, 'hcaptcha_site_key': settings.HCAPTCHA_SITE_KEY}
    return render(request, 'accounts_custom/sign-up.html', context)


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts_custom/sign-in.html'

    def form_valid(self, form):
        user = form.get_user()

        # Verifica se o usuário tem 2FA configurado
        totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if totp_device:
            # Salva o user_id temporariamente na sessão para validar o TOTP depois
            self.request.session['pre_2fa_user_id'] = user.pk
            # Salva o estado da requisição para processar a verificação do OTP
            return redirect('verify_2fa')  # Redireciona para a view de verificação do token

        # Se não tiver 2FA configurado, faz o login normalmente
        login(self.request, user)
        return redirect(self.get_success_url())
    

class UserLoginView(LoginView):
    form_class = LoginForm

    def get_template_names(self):
        # Aqui você retorna o caminho do template com base no tema ativo
        return [resolve_templated_path(self.request, 'accounts_custom', 'sign-in.html')]

    def form_valid(self, form):
        user = form.get_user()

        totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if totp_device:
            self.request.session['pre_2fa_user_id'] = user.pk
            return redirect('verify_2fa')

        login(self.request, user)
        return redirect(self.get_success_url())
       

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts_custom/password-change.html'
    form_class = UserPasswordChangeForm

    def form_valid(self, form):
        print(_("Password changed successfully!"))
        return super().form_valid(form)

    def form_invalid(self, form):
        print(_("Password change failed!"))
        return super().form_invalid(form)
    

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts_custom/forgot-password.html'
    form_class = UserPasswordResetForm

    def form_valid(self, form):
        print(_("Password reset email sent!"))
        return super().form_valid(form)

    def form_invalid(self, form):
        print(_("Failed to send password reset email!"))
        return super().form_invalid(form)
    

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts_custom/reset-password.html'
    form_class = UserSetPasswordForm

    def form_valid(self, form):
        # Apenas atualiza a senha sem mexer em outros campos do modelo
        form.user.set_password(form.cleaned_data['new_password1'])
        form.user.save(update_fields=["password"])  # Evita save completo que pode tentar mexer no avatar
        print(_("Password has been reset!"))
        return super(PasswordResetConfirmView, self).form_valid(form)

    def form_invalid(self, form):
        print(_("Password reset failed!"))
        return super().form_invalid(form)
  