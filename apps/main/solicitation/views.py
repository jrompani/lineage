from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Solicitation, SolicitationHistory, SolicitationParticipant
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import SolicitationForm
from django.contrib import messages
from django.shortcuts import redirect
from utils.notifications import send_notification
from django.urls import reverse
import logging

from apps.main.home.models import PerfilGamer
from utils.services import verificar_conquistas


logger = logging.getLogger(__name__)


def is_staff_or_owner(user, solicitation):
    return user.is_staff or solicitation.user == user


class SolicitationDashboardView(LoginRequiredMixin, View):
    def get(self, request, protocol):
        # Obtém a proposta de crédito pelo protocolo
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Obtém os participantes associados à solicitação
        participants = SolicitationParticipant.objects.filter(solicitation=solicitation)

        # Obtém o histórico de eventos associados à solicitação
        history = SolicitationHistory.objects.filter(solicitation=solicitation).order_by('-timestamp')

        # Passa os dados para o contexto
        context = {
            'solicitation': solicitation,
            'participants': participants,
            'history': history,
        }

        return render(request, 'pages/solicitation_dashboard.html', context)
    

class SolicitationListView(LoginRequiredMixin, ListView):
    model = Solicitation
    template_name = 'pages/solicitation_list.html'  # Substitua pelo seu caminho de template
    context_object_name = 'solicitations'  # Nome da variável que conterá as solicitações no template
    paginate_by = 10  # Número de itens por página

    def get_queryset(self):
        # Verifica se o usuário é admin
        if self.request.user.is_staff:
            # Se for admin, retorna todas as solicitações
            return Solicitation.objects.all()
        else:
            # Se não for admin, retorna apenas as solicitações do usuário logado
            return Solicitation.objects.filter(user=self.request.user)


class SolicitationCreateView(LoginRequiredMixin, CreateView):
    model = Solicitation
    form_class = SolicitationForm
    template_name = 'pages/solicitation_create.html'
    success_url = reverse_lazy('solicitation:solicitation_list')

    def dispatch(self, request, *args, **kwargs):
        if Solicitation.objects.filter(user=request.user, status='pending').exists():
            messages.warning(request, "Você já possui uma solicitação pendente. Aguarde o processamento antes de criar uma nova.")
            return redirect('solicitation:solicitation_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        perfil = PerfilGamer.objects.get(user=self.request.user)
        perfil.adicionar_xp(50)

        # Verifica se alguma conquista foi desbloqueada
        conquistas_desbloqueadas = verificar_conquistas(self.request.user, request=self.request)
        if conquistas_desbloqueadas:
            for conquista in conquistas_desbloqueadas:
                messages.success(self.request, f"🏆 Você desbloqueou a conquista: {conquista.nome}!")

        try:
            # Envia notificação para os staffs
            send_notification(
                user=None,  # None para broadcast para staff
                notification_type='staff',
                message='Relatório sigiloso disponível.',
                created_by=self.request.user,
                link=reverse('solicitation:solicitation_list')
            )
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {str(e)}")

        return response


class AddEventToHistoryView(View):
    def get(self, request, protocol):
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Verifica se o usuário tem permissão
        if not is_staff_or_owner(request.user, solicitation):
            messages.error(request, "Você não tem permissão para adicionar eventos ao histórico dessa solicitação.")
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se há algum evento no histórico e se o último foi de um usuário comum
        last_event = solicitation.solicitation_history.last()
        
        # Se o usuário não for staff, o próximo evento precisa ser registrado por um staff
        if last_event is not None and last_event.user is not None and not request.user.is_staff:
            if not last_event.user.is_staff:
                messages.info(request, "O próximo evento precisa ser registrado por um staff.")
                return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Exibe formulário de evento
        return render(request, 'pages/add_event_to_history.html', {'solicitation': solicitation})

    def post(self, request, protocol):
        solicitation = get_object_or_404(Solicitation, protocol=protocol)

        # Verifica se o usuário tem permissão
        if not is_staff_or_owner(request.user, solicitation):
            messages.error(request, "Você não tem permissão para adicionar eventos ao histórico dessa solicitação.")
            return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Verifica se o último evento foi de um usuário comum, mas permite que staff registre eventos sem restrição
        last_event = solicitation.solicitation_history.last()

        # Se o usuário não for staff, o próximo evento precisa ser registrado por um staff
        if last_event is not None and last_event.user is not None and not request.user.is_staff:
            if not last_event.user.is_staff:
                messages.error(request, "Você só pode registrar um evento depois que um staff fizer a próxima alteração.")
                return redirect('solicitation:solicitation_dashboard', protocol=protocol)

        # Adiciona evento ao histórico
        action = request.POST.get('action')
        image = request.FILES.get('image')

        # Cria o evento com o usuário que fez a alteração
        SolicitationHistory.objects.create(
            solicitation=solicitation,
            action=action,
            image=image,
            user=request.user  # Associando o usuário que fez a alteração
        )

        messages.success(request, "Evento registrado com sucesso.")
        return redirect('solicitation:solicitation_dashboard', protocol=protocol)
