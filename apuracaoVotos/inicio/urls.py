from django.urls import path
from . import views

app_name = 'inicio'  # Define o namespace 'inicio'

urlpatterns = [
    path('', views.home),
    path('votacao/', views.menu, name='votacao'),
    path('urnas/', views.urnas, name='urnas'),
    path('candidatos/', views.candidatos, name='candidatos'),
    path('get_sessoes/', views.get_sessoes, name='get_sessoes'),
    path('importacao/', views.post_importar, name='post_importacao'),
    path('inicializa_votacao/', views.inicializa_votacao, name='inicializa_votacao'),
    path('configuracao_sessao/', views.configuracao_sessao, name='configuracao_sessao'),
]
