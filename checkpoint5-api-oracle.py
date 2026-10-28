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
        "poder_total": (item.get("atkMax") + item.get("hpMax")),
        "categoria_raridade": (definirCategoria(item.get("rarity")))
    }


def obter_personagens():
    """Devolve a lista de personagens jogáveis já com os campos extraídos."""
    # collectionNo = 0 são inimigos/NPCs, então ficam de fora
    return [extrair_dados_personagem(i) for i in buscar_servants()
            if isinstance(i, dict) and i.get("collectionNo")]

def imprimirDados(item):
    print(f'\nid: {item["id_personagem"]}\nNumero coleção: {item["numero_colecao"]}\nNome: {item["nome"]}\nClasse: {item["classe"]}\nRaridade: {item["raridade"]}\nCusto: {item["custo"]}\nNivel Maximo: {item["nivel_max"]}\nAtaque Maximo: {item["ataque_max"]}\nVida Maxima: {item["vida_max"]}\nAtributo: {item["atributo"]}\nPoder Total: {item["poder_total"]}\nCategoria por Raridade: {item["categoria_raridade"]}\n')


if __name__ == "__main__":
    lista = obter_personagens()
    print(f"{len(lista)} personagens recebidos.")
    if lista:
        for i in range(5):
             item = lista[i]
             imprimirDados(item)
