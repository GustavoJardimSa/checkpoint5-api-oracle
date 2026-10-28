"""
Checkpoint 5 - Parte A: Consumo de API Pública (requests)
API: Atlas Academy API (https://api.atlasacademy.io) - dados de Fate/Grand Order
Dados usados: apenas os personagens (servants) da versão NA do jogo.
"""

import requests

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


def extrair_dados_personagem(item):
    """Pega um personagem do JSON e devolve um dicionário simples."""
    return {
        "id_personagem": item.get("id"),
        "numero_colecao": item.get("collectionNo"),
        "nome": item.get("name"),
        "classe": item.get("className"),
        "raridade": item.get("rarity"),
        "custo": item.get("cost"),
        "nivel_max": item.get("lvMax"),
        "ataque_max": item.get("atkMax"),
        "vida_max": item.get("hpMax"),
        "atributo": item.get("attribute"),
    }


def obter_personagens():
    """Devolve a lista de personagens jogáveis já com os campos extraídos."""
    # collectionNo = 0 são inimigos/NPCs, então ficam de fora
    return [extrair_dados_personagem(i) for i in buscar_servants()
            if isinstance(i, dict) and i.get("collectionNo")]


if __name__ == "__main__":
    lista = obter_personagens()
    print(f"{len(lista)} personagens recebidos.")
    if lista:
        print(lista[0])
