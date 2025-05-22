from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.protocol import create_protocol
from apps.main.home.models import User
from core.models import BaseModel
from .choices import STATUS_CHOICES


class Solicitation(BaseModel):
    protocol = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name=_("Protocolo"),
        help_text=_("Código de identificação único da solicitação.")
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Status"),
        help_text=_("Status atual da solicitação.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='solicitations_user',
        blank=True,
        null=True,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que iniciou a solicitação.")
    )

    def add_participant(self, user):
        """Adiciona um participante à proposta."""
        SolicitationParticipant.objects.get_or_create(solicitation=self, user=user)

    def is_participant(self, user):
        """Verifica se o usuário é um dos participantes da proposta."""
        return SolicitationParticipant.objects.filter(solicitation=self, user=user).exists()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.protocol:
            self.protocol = create_protocol()
        super().save(*args, **kwargs)

        if is_new and self.user:
            SolicitationParticipant.objects.get_or_create(solicitation=self, user=self.user)

        SolicitationHistory.objects.create(solicitation=self, action=_('Solicitação criada.'))

    def __str__(self):
        return f"{_('Solicitação')} {self.protocol} - {self.status}"

    class Meta:
        verbose_name = _("Solicitação")
        verbose_name_plural = _("Solicitações")


class SolicitationParticipant(BaseModel):
    solicitation = models.ForeignKey(
        Solicitation,
        on_delete=models.CASCADE,
        related_name='solicitation_participants',
        verbose_name=_("Solicitação")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitations_users',
        verbose_name=_("Usuário")
    )

    def __str__(self):
        return f'{self.user.username} - {self.solicitation.protocol}'

    class Meta:
        verbose_name = _("Participante da Solicitação")
        verbose_name_plural = _("Participantes da Solicitação")
        unique_together = ('solicitation', 'user')


class SolicitationHistory(BaseModel):
    solicitation = models.ForeignKey(
        Solicitation,
        on_delete=models.CASCADE,
        related_name='solicitation_history',
        verbose_name=_("Solicitação")
    )
    action = models.CharField(
        max_length=255,
        verbose_name=_("Ação"),
        help_text=_("Descrição da ação realizada.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data e Hora"),
        help_text=_("Momento em que a ação foi registrada.")
    )
    image = models.ImageField(
        upload_to='solicitation_history_images/',
        null=True,
        blank=True,
        verbose_name=_("Imagem"),
        help_text=_("Imagem opcional associada à ação.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que realizou a ação.")
    )

    def __str__(self):
        return f"{_('Histórico da Solicitação')} {self.solicitation.protocol} - {self.timestamp}"

    class Meta:
        verbose_name = _("Histórico da Solicitação")
        verbose_name_plural = _("Históricos da Solicitação")
