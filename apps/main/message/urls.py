from django.urls import path
from .views import *


app_name = 'message'


urlpatterns = [
    path('index/', message, name='index'),
    path('send-friend-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:friendship_id>/', reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<int:friendship_id>/', remove_friend, name='remove_friend'),
    path('friends-list/', friends_list, name='friends_list'),

    path('api/send-message/', send_message, name='send_message'),
    path('api/load-messages/<int:friend_id>/', load_messages, name='load_messages'),
    path('api/get_unread_count/', get_unread_count, name='unread_count'),
    path('api/set-user-active/', set_user_active, name='set_user_active'),
    path('api/check-user-activity/<int:user_id>/', check_user_activity, name='check_user_activity'),
]
