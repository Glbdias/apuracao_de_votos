from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

estados = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'
}


def home(request):
    return render(request, 'home.html')


def menu(request):
    return render(request, 'base.html')


def urnas(request):
    dic = {'estados': estados}
    return render(request, 'apuracao_urnas.html', dic)


def candidatos(request):
    return render(request, 'candidatos.html')


def get_votos(request):
    if request.method == "GET":
        # Simulação de dados dos votos
        votos = [
            {"candidato": "Candidato 1", "votos": 3500, "percentual": "35%"},
            {"candidato": "Candidato 2", "votos": 2750, "percentual": "27.5%"},
            {"candidato": "Candidato 3", "votos": 1200, "percentual": "12%"},
            {"candidato": "Candidato 4", "votos": 950, "percentual": "9.5%"}
        ]
        return JsonResponse({"votos": votos})


def post_importar(request):
    return render(request, 'importacao.html')
