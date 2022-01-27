from django.urls import path
from . import anime_views
from . import character_views
from . import genre_views
from . import mailing_views

urlpatterns = [

    # anime subscription urls

    path('anime/<str:slug>/subscribe',
         mailing_views.AnimeSubscribeView.as_view(), name='anime-subscribe'),
    path('anime/<str:slug>/unsubscribe',
         mailing_views.AnimeUnsubscribeView.as_view(), name='anime-unsubscribe'),

    # mailing list urls

    path('subscribe',
         mailing_views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe',
         mailing_views.UnsubscribeView.as_view(), name='unsubscribe'),

    # send mail urls

    path('anime/<str:slug>/mail',
         mailing_views.SendMailView.as_view(), name='mail-subscribers'),
    path('anime/<str:slug>/celerymail',
         mailing_views.CeleryMailView.as_view(), name='celery-mail-subscribers'),
    path('anime/<str:slug>/schedule',
         mailing_views.ScheduleMail.as_view(), name='schedule-mail'),


    # anime CRUD urls

    path('anime/', anime_views.AnimeListView.as_view(), name='anime-list'),
    path('anime/create', anime_views.AnimeCreateView.as_view(), name='anime-create'),
    path('anime/<str:slug>', anime_views.AnimeDetailView.as_view(),
         name='anime-detail'),
    path('anime/<str:slug>/update',
         anime_views.AnimeUpdateView.as_view(), name='anime-update'),
    path('anime/<str:slug>/delete',
         anime_views.AnimeDeleteView.as_view(), name='anime-delete'),


    # genre CRUD urls

    path('genre/', genre_views.GenreListView.as_view(), name='genre-list'),
    path('genre/create', genre_views.GenreCreateView.as_view(), name='genre-create'),
    path('genre/<str:slug>', genre_views.GenreDetailView.as_view(),
         name='genre-detail'),
    path('genre/<str:slug>/update',
         genre_views.GenreUpdateView.as_view(), name='genre-update'),
    path('genre/<str:slug>/delete',
         genre_views.GenreDeleteView.as_view(), name='genre-delete'),

    # character CRUD urls

    path('character/', character_views.CharacterListView.as_view(),
         name='character-list'),
    path('character/create', character_views.CharacterCreateView.as_view(),
         name='character-create'),
    path('character/<str:slug>', character_views.CharacterDetailView.as_view(),
         name='character-detail'),
    path('character/<str:slug>/update',
         character_views.CharacterUpdateView.as_view(), name='character-update'),
    path('character/<str:slug>/delete',
         character_views.CharacterDeleteView.as_view(), name='character-delete'),

]
