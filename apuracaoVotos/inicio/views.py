import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import json

locais = {
    "TOD": "Todos os dados",
    "CCN": "Centro Cultural Caxias do Sul",
    "CMD": "Câmara Municipal de Caxias do Sul",
    "EMP": "Escola Municipal Professor Abelardo",
    "CED": "Colégio Estadual Caxias do Sul",
    "CCD": "Centro de Convenções de Caxias do Sul",
    "SDC": "Sesc Caxias do Sul",
    "PDP": "Praça Dante Alighieri",
    "CSD": "Centro de Saúde Caxias do Sul",
    "PNU": "Parque Natural Caxias do Sul",
    "FDC": "Faculdade Caxias do Sul",
    "BMD": "Biblioteca Municipal Caxias do Sul",
    "EMF": "Estádio Municipal Caxias do Sul",
    "AMB": "Associação de Moradores Bairro Pioneiro",
    "HMD": "Hospital Municipal Caxias do Sul",
    "CCX": "Clube Caxias",
    "SCX": "Shopping Caxias do Sul",
    "USS": "Unidade de Saúde São José",
    "IMN": "Igreja Matriz de Caxias do Sul",
    "CEA": "Complexo Esportivo Alvorada",
    "CEP": "Centro de Eventos de Caxias do Sul"
}


def home(request):
    request.session['locais'] = {}
    request.session['totais'] = 0
    request.session['votos_apurados'] = 0
    request.session['zonas'] = {}
    request.session.modified = True
    return render(request, 'home.html')


def menu(request):
    return render(request, 'base.html')


def urnas(request):
    dic = {'estados': locais, 'totalVotos': request.session['totais'],
           'votosApurados': request.session['votos_apurados'], 'zonas': request.session['configuracao'].keys()}
    return render(request, 'apuracao_urnas.html', dic)


def candidatos(request):
    return render(request, 'candidatos.html')


def get_sessoes(request):
    ses = request.session['configuracao'][request.GET['zona'].strip()]['sessoes'].keys()
    qtdZonas = 0
    print(request.session['configuracao'][request.GET['zona'].strip()]['sessoes']['001A']['votos'])
    if request.GET.get('zona') and request.GET.get('sessao'):
        qtdZonas = request.session['configuracao'][request.GET['zona'].strip()]['sessoes'][request.GET['sessao'].strip()]['votos']
    elif request.GET['zona']:
        qtdZonas = request.session['configuracao'][request.GET['zona'].strip()]['total_votos']

    sessoes = []
    for i in ses:
        sessoes.append(i)

    return JsonResponse({"sessoes": sessoes, 'qtdVotosApurados': qtdZonas})


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

    for i in json_data:
        est.session['configuracao'][i['idZona']]['total_votos'] += i['votosValidos']
        est.session['votos_apurados'] += i['votosValidos']
        est.session['configuracao'][i['idZona']]['sessoes'][i['idSecao']]['votos'] += i['votosValidos']

    est.session.modified = True

    # for locais in json_data:
    #     if not est.session['locais'].get(locais['nomeLocal']):
    #         est.session['locais'][locais['nomeLocal']] = {'total_votos': 0}
    #
    #     est.session['locais'][locais['nomeLocal']]['total_votos'] += locais['votosSessao']
    #     est.session['totais'] += locais['votosSessao']
    #
    # est.session.modified = True


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
                dic[i['idZona']] = {'total_votos': 0, 'sessoes': {}}

            for p in i['secoes']:
                if not dic[i['idZona']]['sessoes'].get(p['idSecao']):
                    dic[i['idZona']]['sessoes'][p['idSecao']] = {'quantidadeEleitores': p['quantidadeEleitores'], 'votos': 0}

                    ent.session['totais'] += p['quantidadeEleitores']

        ent.session['configuracao'] = dic

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
