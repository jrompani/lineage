from django.urls import path
from .views.server_views import *
from .views.accounts_views import *
from .views.config_views import *
from .views.tops_views import *
from .views.status_views import *
from .views.services_views import *

app_name = 'server'

urlpatterns = [
    path("api/players-online/", players_online, name="api_players_online"),
    path("api/top-pvp/", top_pvp, name="api_top_pvp"),
    path("api/top-pk/", top_pk, name="api_top_pk"),
    path("api/top-clan/", top_clan, name="api_top_clan"),
    path("api/top-rich/", top_rich, name="api_top_rich"),
    path("api/top-online/", top_online, name="api_top_online"),
    path("api/top-level/", top_level, name="api_top_level"),
    path("api/olympiad-ranking/", olympiad_ranking, name="api_olympiad_ranking"),
    path("api/olympiad-heroes/", olympiad_all_heroes, name="api_olympiad_all_heroes"),
    path("api/olympiad-current-heroes/", olympiad_current_heroes, name="api_olympiad_current_heroes"),
    path("api/grandboss-status/", grandboss_status, name="api_grandboss_status"),
    path("api/siege/", siege, name="api_siege"),
    path("api/siege-participants/<int:castle_id>/", siege_participants, name="api_siege_participants"),
    path("api/boss-jewel-locations/", boss_jewel_locations, name="api_boss_jewel_locations"),

    path("api/config/", api_config_panel, name="api_config_panel"),

    path('account/update-password/', update_password, name='update_password'),
    path('account/dashboard/', account_dashboard, name='account_dashboard'),
    path('account/register/', register_lineage_account, name='lineage_register'),
    path('account/register/success/', register_success, name='register_success'),

    path('status/top-pvp/', top_pvp_view, name='top_pvp'),
    path('status/top-pk/', top_pk_view, name='top_pk'),
    path('status/top-adena/', top_adena_view, name='top_adena'),
    path('status/top-clans/', top_clans_view, name='top_clans'),
    path('status/top-level/', top_level_view, name='top_level'),
    path("status/top-online/", top_online_view, name="top_online"),

    path("status/siege-ranking/", siege_ranking_view, name="siege_ranking"),
    path('status/olympiad-ranking/', olympiad_ranking_view, name='olympiad_ranking'),
    path('status/olympiad-all-heroes/', olympiad_all_heroes_view, name='olympiad_all_heroes'),
    path('status/olympiad-current-heroes/', olympiad_current_heroes_view, name='olympiad_current_heroes'),
    path('status/boss-jewel-locations/', boss_jewel_locations_view, name='boss_jewel_locations'),
    path('status/grandboss/', grandboss_status_view, name='grandboss_status'),

    path('account/change-sex/<int:char_id>/', change_sex_view, name='change_sex'),
    path('account/unstuck/<int:char_id>/', unstuck_view, name='unstuck'),
    path('account/change-nickname/<int:char_id>/', change_nickname_view, name='change_nickname'),
    path('account/configure-service-prices/', configure_service_prices, name='configure_service_prices'),
    path('account/link-lineage-account/', link_lineage_account, name='link_lineage_account'),
    path('account/link-by-email/', request_link_by_email, name='request_link_by_email'),
    path('account/link-by-email/<str:token>/', link_by_email_token, name='link_by_email_token'),

    path('supporter/panel/', painel_apoiador, name='painel_apoiador'),
    path('supporter/request/', formulario_apoiador, name='formulario_apoiador'),
    path('supporter/panel/staff/', painel_staff, name='painel_staff'),
    path('supporter/request-commission/', solicitar_comissao, name='solicitar_comissao'),
    path('supporter/panel/edit-image/', editar_imagem_apoiador, name='editar_imagem_apoiador'),
]
