"""
Checkpoint 5 - Parte A: Consumo de API Pública (requests)
API: Atlas Academy API (https://api.atlasacademy.io) - dados de Fate/Grand Order
Dados usados: apenas os personagens (servants) da versão NA do jogo.
"""

import requests
import random

URL = "https://api.atlasacademy.io/export/NA/basic_servant.json"


def buscar_servants():
    """Faz o GET na API e devolve o JSON (lista vazia se der erro)."""
    try:
        resposta = requests.get(URL, timeout=30)
    except requests.exceptions.Timeout:
        print("Erro: a API demorou demais para responder.")
        return []
    except requests.exceptions.RequestException as erro:
        print(f"Erro de conexão: {erro}")
        return []

    if resposta.status_code == 404:
        print("Erro 404: recurso não encontrado.")
    elif resposta.status_code == 500:
        print("Erro 500: problema no servidor da API.")
    elif resposta.status_code != 200:
        print(f"Erro HTTP {resposta.status_code}: {resposta.text[:200]}")
    else:
        dados = resposta.json()
        if isinstance(dados, list):
            return dados
        print(f"Erro: formato inesperado da API: {str(dados)[:300]}")
    return []

def definirCategoria(raridade):
    if (raridade >= 1 and raridade <= 3):
            categoriaRaridade = 'Comum'
    elif (raridade == 4):
            categoriaRaridade = 'Raro'
    else:
            categoriaRaridade = 'Ultra raro'
    return categoriaRaridade

def extrair_dados_personagem(item):
    """Pega um personagem do JSON e devolve um dicionário simples."""
    return {
        "id_personagem": item.get("collectionNo"),
        "nome": item.get("name"),
        "classe": item.get("className"),
        "raridade": item.get("rarity"),
        "ataque_max": item.get("atkMax"),
        "vida_max": item.get("hpMax"),
        "atributo": item.get("attribute"),
        "poder_total": (item.get("atkMax") + item.get("hpMax")),
        "categoria_raridade": (definirCategoria(item.get("rarity")))
    }


def obter_personagens():
    """Devolve a lista de personagens jogáveis já com os campos extraídos."""
    # collectionNo = 0 são inimigos/NPCs, então ficam de fora
    return [extrair_dados_personagem(i) for i in buscar_servants()
            if isinstance(i, dict) and i.get("collectionNo")]

def imprimirDados(item):
    print(f'\nId: {item["id_personagem"]}\nNome: {item["nome"]}\nClasse: {item["classe"]}\nRaridade: {item["raridade"]}\nAtaque Maximo: {item["ataque_max"]}\nVida Maxima: {item["vida_max"]}\nAtributo: {item["atributo"]}\nPoder Total: {item["poder_total"]}\nCategoria por Raridade: {item["categoria_raridade"]}\n')

def escolhaIndice(lista):
    try:
        indice = int(input(f'digite o indice desejado (1 - {len(lista)}): '))
    except ValueError:
        print('\nDigite apenas numeros inteiros\n')
    else:
        if(indice >= 1 and indice <= (len(lista))):
            imprimirDados(lista[indice - 1])
        else:
            print('\nindice inválido\n')

def escolhaIntervalo(lista):
    try:
        indiceInicial = int(input('Escolha o indice inicial: '))
        indiceFinal = int(input('Escolha o indice final: '))
    except ValueError:
        print('\nDigite apenas numeros inteiros\n')
    else:
        if(indiceInicial < 1):
            print('\no indice inicial não pode ser menor que 1\n')
        elif(indiceInicial > len(lista) or indiceFinal > len(lista)):
            print('\nO indice não pode ser maior que a lista\n')
        elif(indiceInicial > indiceFinal):
            print('\nEscolha inválida, o indice inicial deve ser menor que o final\n')
        elif(indiceInicial == indiceFinal):
            print('\nEscolha inválida, os dois indices não podem ser iguais\n')
        else:
            for i in range((indiceInicial - 1), (indiceFinal)):
                imprimirDados(lista[i])

def escolhaAleatória(lista):
    indicesSorteados = []
    while len(indicesSorteados) < 5:
        indice = random.randint(0,(len(lista) - 1))
        if(indice not in indicesSorteados):
            indicesSorteados.append(indice)
    for i in indicesSorteados:
        imprimirDados(lista[i])

def main():
    lista = obter_personagens()
    print(f"{len(lista)} personagens recebidos.")
    if lista:
        while True:
            print('Ações:\n1 - Escolha por indice\n2 - Escolha por intervalo\n3 - 5 escolhas aleatórias\n0 - sair')
            try:
                escolha = int(input('Escolha uma Ação: '))
            except ValueError:
                print('\nDigite apenas numeros inteiros\n')
            else:
                if(escolha == 0):
                    break
                elif(escolha == 1):
                    escolhaIndice(lista)
                elif(escolha == 2):
                    escolhaIntervalo(lista)
                elif(escolha == 3):
                    escolhaAleatória(lista)
                else:
                    print('\nEscolha inválida\n')

                

main()