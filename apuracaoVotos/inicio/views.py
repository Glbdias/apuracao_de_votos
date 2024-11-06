from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def menu(request):
    return render(request, 'base.html')


def urnas(request):
    return render(request, 'apuracao_urnas.html')


def candidatos(request):
    return render(request, 'candidatos.html')
