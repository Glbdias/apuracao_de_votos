import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import VotosCandidatos


def home(request):
    request.session['locais'] = {}
    request.session['totais'] = 0
    request.session['totais_abstencao'] = 0
    request.session['votos_apurados'] = 0
    request.session['total_sessoes'] = 0
    request.session['sessoes_importadas'] = 0
    request.session['zonas'] = {}
    request.session.modified = True
    limpar_dados()
    return render(request, 'home.html')


def menu(request):
    dic = {'nome_eleicao': request.session['nomeEleicao']}
    return render(request, 'base.html', dic)


def urnas(request):
    valor: float = calcula_percentual(request.session['totais'], request.session['votos_apurados'])
    dic = {'totalVotos': request.session['totais'], 'abstencao': request.session['totais_abstencao'],
           'votosApurados': request.session['votos_apurados'], 'zonas': request.session['configuracao'].keys(),
           'nome_eleicao': request.session['nomeEleicao'], 'total_sessoes': request.session['total_sessoes'],
           'sessoes_importadas': request.session['sessoes_importadas'],
           'percentual_sessao': calcula_percentual(request.session['total_sessoes'],
                                                   request.session['sessoes_importadas']),
           'percentual_votos': f"{valor:.2f}"}
    return render(request, 'apuracao_urnas.html', dic)


def candidatos(request):

    dic = {'candidatos': get_candidatos(request)}
    return render(request, 'candidatos.html', dic)


def get_sessoes(request):
    try:
        if (not request.GET.get('zona') and not request.GET.get('sessao')) or not request.GET.get('zona'):
            return JsonResponse(
                {"sessoes": [], 'qtdVotosApurados': request.session['votos_apurados'], 'qtdAbstencaoApurados': 0,
                 'status': 200,
                 'percentual': f"{calcula_percentual(request.session['totais'], request.session['votos_apurados']):.2f}"})
        ses = request.session['configuracao'][request.GET['zona'].strip()]['sessoes'].keys()
        qtdZonas = 0
        qtd_abstencao = 0
        percentual = 0
        if request.GET.get('zona') and request.GET.get('sessao'):
            qtdZonas = \
                request.session['configuracao'][request.GET['zona'].strip()]['sessoes'][request.GET['sessao'].strip()][
                    'votos']
            qtd_abstencao = \
                request.session['configuracao'][request.GET['zona'].strip()]['sessoes'][request.GET['sessao'].strip()][
                    'abstencao']
        elif request.GET['zona']:
            qtdZonas = request.session['configuracao'][request.GET['zona'].strip()]['total_votos']
            qtd_abstencao = request.session['configuracao'][request.GET['zona'].strip()]['abstencao']

        sessoes = []
        for i in ses:
            sessoes.append(i)

        return JsonResponse({"sessoes": sessoes, 'qtdVotosApurados': qtdZonas, 'qtdAbstencaoApurados': qtd_abstencao,
                             'status': 200,
                             'percentual': f"{calcula_percentual(request.session['totais'], qtdZonas):.2f}"})
    except KeyError as e:
        erro = f"A chave '{e.args[0]}' não foi encontrada na apuração dos votos."
        return JsonResponse(
            {'status': 400, 'chave': erro, 'qtdVotosApurados': 0, 'qtdAbstencaoApurados': 0, 'sessoes': []})


def post_importar(request):
    retorno = {'sucesso': True,
               'mensagem': ''}
    if request.method == "POST":
        organiza_arquivo(request.FILES['file'], request)
        return JsonResponse(retorno)
    return render(request, 'importacao.html')


def inicializa_votacao(request):
    dic = {'status': True,
           'mensagem': ''}

    if request.method == 'POST':
        request.session['votos'] = {'candidateCount': request.POST['candidateCount'],
                                    'expectedVotes': request.POST['expectedVotes']}

        dic['mensagem'] = 'Cadastro efetuado com sucesso!'

        request.session.modified = True
        return render(request, 'importacao.html')

    return render(request, 'inicializacao.html', dic)


def transformar_arquivo_python(nome):
    """
    Tranforma arquivo inserido para uma forma como o python compreenda
    :return:
    """
    with open(nome, 'r') as file:
        return json.load(file)


def organiza_arquivo(arquivo, est):
    file_content = arquivo.read().decode('utf-8')  # Converte de bytes para string
    json_data = json.loads(file_content)  # Converte a string para um dicionário Python

    print(json_data)

    for i in json_data:
        est.session['sessoes_importadas'] += 1
        est.session['configuracao'][i['idZona']]['total_votos'] += i['votosValidos']
        est.session['configuracao'][i['idZona']]['abstencao'] += (i['quantidadePresentes'] - i['votosValidos'])
        est.session['votos_apurados'] += i['votosValidos']
        est.session['totais_abstencao'] += (i['quantidadePresentes'] - i['votosValidos'])
        est.session['configuracao'][i['idZona']]['sessoes'][i['idSecao']]['votos'] += i['votosValidos']
        est.session['configuracao'][i['idZona']]['sessoes'][i['idSecao']]['abstencao'] += (
                i['quantidadePresentes'] - i['votosValidos'])

        for p in i['candidatos']:
            candidatos = VotosCandidatos.objects.get_or_create(nome=p['nomeCandidato'],
                                                               sessao=i['idSecao'],
                                                               zona=i['idZona'])

            candidatos[0].votos += p['quantidadeVotos']
            candidatos[0].save()

    est.session.modified = True


def configuracao_sessao(request):
    retorno = {'sucesso': True,
               'mensagem': ''}
    if request.method == "POST":
        retorno = organiza_configuracao_apuracao(request.FILES['file'], request)
        return JsonResponse(retorno)
    return render(request, 'configuracao.html')


def organiza_configuracao_apuracao(dado, ent):
    """
    Função responsável por organizar os dados de configuração
    :param request:
    :return:
    """

    retorno = {'sucesso': True,
               'mensagem': '',
               'status': 200}
    try:
        file_content = dado.read().decode('utf-8')
        json_data = json.loads(file_content)
        ent.session['nomeVotação'] = json_data['nomeEleicao']
        ent.session['candidatos'] = json_data['candidatos']

        dic = {}
        for i in json_data['zonasEleitorais']:
            if not dic.get(i['idZona']):
                dic[i['idZona']] = {'total_votos': 0, 'sessoes': {}, 'abstencao': 0}

            for p in i['secoes']:
                ent.session['total_sessoes'] += 1
                if not dic[i['idZona']]['sessoes'].get(p['idSecao']):
                    dic[i['idZona']]['sessoes'][p['idSecao']] = {'quantidadeEleitores': p['quantidadeEleitores'],
                                                                 'votos': 0,
                                                                 'abstencao': 0}

                    ent.session['totais'] += p['quantidadeEleitores']

        ent.session['configuracao'] = dic
        ent.session['nomeEleicao'] = json_data['nomeEleicao']

        ent.session.modified = True
        retorno['mensagem'] = 'Arquivo processado com sucesso'

    except KeyError as e:
        retorno['sucesso'] = False
        retorno['mensagem'] = f"A chave '{e.args[0]}' não foi encontrada no JSON."
        retorno['status'] = 400

    except:
        retorno['sucesso'] = False
        retorno['mensagem'] = 'Ocorreu um erro processar arquivo'
        retorno['status'] = 400

    return retorno


def calcula_percentual(total, votos):
    percentual = (votos * 100) / total

    return float(percentual)


def limpar_dados():
    # Limpa todos os dados da tabela 'Usuario'
    VotosCandidatos.objects.all().delete()


def get_candidatos(est):
    retorno = {
        "totalVotosValidos": 0,
        "percentualVotosValidos": 0,
        "candidatos": [
        ]
    }
    import sqlite3

    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('db.sqlite3')

    # Criar um cursor
    cursor = conn.cursor()

    cursor.execute(f"""SELECT
                    nome,
                    SUM(votos),
                    ROUND((SUM(votos) * 100.0) /{est.session['totais']} , 2) AS percentual
                FROM
                    inicio_votoscandidatos
                GROUP BY
                    nome;
    """)

    resultado = cursor.fetchall()
    for i in resultado:
        retorno['totalVotosValidos'] += i[1]
        retorno['percentualVotosValidos'] = f"{(retorno['totalVotosValidos'] * 100)/est.session['totais']:.2f}"
        retorno['candidatos'].append({
            "nomeCandidato": i[0],
            "quantidadeVotos": i[1],
            "percentualVotos": i[2]
        })

    conn.close()

    return retorno
