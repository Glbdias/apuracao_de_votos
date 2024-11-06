from django.urls import path
from . import views

app_name = 'inicio'  # Define o namespace 'inicio'

urlpatterns = [
    path('', views.home),
    path('votacao/', views.menu, name='votacao'),
    path('urnas/', views.urnas, name='urnas'),
    path('candidatos/', views.candidatos, name='candidatos')
]
