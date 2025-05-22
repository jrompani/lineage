from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from apps.main.home.decorator import conditional_otp_required
from .models import Notification, PublicNotificationView
from django.core.paginator import Paginator


@conditional_otp_required
def get_notifications(request):
    # Notificações privadas do usuário (exclui staff se user não for staff/superuser)
    user_notifications = Notification.objects.filter(
        user=request.user,
        viewed=False
    ).exclude(
        notification_type='staff'
    ).order_by('-created_at')

    if request.user.is_staff or request.user.is_superuser:
        # Se for staff/superuser, incluir também notificações staff pra ele
        staff_notifications = Notification.objects.filter(
            user=request.user,
            notification_type='staff',
            viewed=False
        ).order_by('-created_at')
        user_notifications = user_notifications | staff_notifications

    # Notificações públicas
    public_notifications = Notification.objects.filter(
        user=None,
        created_at__gte=request.user.date_joined
    ).order_by('-created_at')

    # Filtra notificações públicas staff apenas para usuários staff/superusers
    if not (request.user.is_staff or request.user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    # Visualizações públicas
    public_notifications_viewed = PublicNotificationView.objects.filter(user=request.user, viewed=True)
    public_notifications_viewed_ids = [pnv.notification.id for pnv in public_notifications_viewed]

    notifications_list = []

    # Notificações privadas
    for notification in user_notifications:
        notifications_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'viewed': notification.viewed,
            'detail_url': reverse('notification:notification_detail', args=[notification.id])
        })

    # Notificações públicas
    for notification in public_notifications:
        if notification.id not in public_notifications_viewed_ids:
            notifications_list.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'viewed': False,
                'detail_url': reverse('notification:notification_detail', args=[notification.id])
            })

    return JsonResponse({'notifications': notifications_list})


@conditional_otp_required
def mark_all_as_read(request):
    # Marcar todas as notificações privadas como lidas
    Notification.objects.filter(user=request.user, viewed=False).update(viewed=True)

    # Buscar notificações públicas válidas para este usuário
    public_notifications = Notification.objects.filter(
        user=None,
        created_at__gte=request.user.date_joined
    )

    if not (request.user.is_staff or request.user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    for notification in public_notifications:
        public_notification_view, created = PublicNotificationView.objects.get_or_create(
            user=request.user,
            notification=notification
        )
        if not public_notification_view.viewed:
            public_notification_view.viewed = True
            public_notification_view.save()

    return JsonResponse({'status': 'ok'})


@conditional_otp_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})


@conditional_otp_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    # Proteção: usuário comum tentando acessar notificação staff
    if notification.notification_type == 'staff' and not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=400)

    # Garante que só o dono (ou notificação pública) pode visualizar
    if notification.user == request.user:
        notification.viewed = True
        notification.save()

    elif notification.user is None:
        public_notification_view = PublicNotificationView.objects.filter(
            user=request.user,
            notification=notification
        ).first()
        if not public_notification_view:
            PublicNotificationView.objects.create(
                user=request.user,
                notification=notification,
                viewed=True
            )

    else:
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=400)

    data = {
        'type': notification.get_notification_type_display(),
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'link': notification.link if notification.link else None,
    }

    return JsonResponse(data)


@conditional_otp_required
def all_notifications(request):
    user = request.user

    # Private notifications
    private_qs = Notification.objects.filter(user=user).order_by('-created_at')
    if not (user.is_staff or user.is_superuser):
        private_qs = private_qs.exclude(notification_type='staff')

    # Public notifications
    public_qs = Notification.objects.filter(user=None).order_by('-created_at')
    if not (user.is_staff or user.is_superuser):
        public_qs = public_qs.exclude(notification_type='staff')

    # Viewed public notifications
    viewed_public_ids = set(
        PublicNotificationView.objects.filter(user=user).values_list('notification_id', flat=True)
    )

    # Marcar instância como visualizada
    for n in public_qs:
        n.viewed = n.id in viewed_public_ids

    # Paginação
    private_paginator = Paginator(private_qs, 10)
    public_paginator = Paginator(public_qs, 10)

    private_page_number = request.GET.get('private_page')
    public_page_number = request.GET.get('public_page')

    private_notifications = private_paginator.get_page(private_page_number)
    public_notifications = public_paginator.get_page(public_page_number)

    context = {
        'private_notifications': private_notifications,
        'public_notifications': public_notifications,
        'segment': 'index',
        'parent': 'notification',
    }
    return render(request, 'pages/notifications.html', context)


@conditional_otp_required
def confirm_notification_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.user == request.user:
        notification.viewed = True
        notification.save()
    elif notification.user is None:
        # Verifica se existe uma marcação de visualização para notificação pública
        public_notification_view, created = PublicNotificationView.objects.get_or_create(user=request.user, notification=notification)
        if created:
            public_notification_view.viewed = True
            public_notification_view.save()

    return JsonResponse({'status': 'success'})
