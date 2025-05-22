import logging
from django.shortcuts import redirect
from django.urls import reverse


logger = logging.getLogger(__name__)


class ForbiddenRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        login_url = reverse('login')
        if response.status_code == 403 and request.path != login_url:
            # Log para verificar de onde vem o erro 403
            logger.warning(f'Erro 403: Acesso negado para {request.path} por {request.user}')
            # Redirecionamento para a página de login
            return redirect(login_url)
        return response
    