"""
Checkpoint 5 - Parte A: Consumo de API Pública (requests)
API: REST Countries (https://restcountries.com)
"""

import requests

URL_BASE = "https://restcountries.com/v3.1/all"
CAMPOS = "cca3,name,capital,region,subregion,population,area,currencies,languages"


def buscar_paises():
    """Faz o GET na API e devolve o JSON bruto (lista vazia se der erro)."""
    try:
        resposta = requests.get(URL_BASE, params={"fields": CAMPOS}, timeout=10)
    except requests.exceptions.Timeout:
        print("Erro: a API demorou demais para responder (timeout).")
        return []
    except requests.exceptions.ConnectionError:
        print("Erro: falha de conexão. Verifique a internet.")
        return []
    except requests.exceptions.RequestException as erro:
        print(f"Erro inesperado na requisição: {erro}")
        return []

    # Tratamento dos status HTTP
    if resposta.status_code == 200:
        try:
            return resposta.json()
        except ValueError:
            print("Erro: a API retornou um JSON inválido.")
            return []
    elif resposta.status_code == 404:
        print("Erro 404: recurso não encontrado.")
    elif resposta.status_code == 500:
        print("Erro 500: problema no servidor da API.")
    else:
        print(f"Erro HTTP {resposta.status_code}")
    return []


def extrair_dados_pais(item):
    """Pega um país do JSON e devolve um dicionário simples."""
    capitais = item.get("capital", [])
    moedas = item.get("currencies", {})
    idiomas = item.get("languages", {})

    return {
        "codigo_pais": item.get("cca3"),
        "nome_comum": item["name"]["common"],
        "nome_oficial": item["name"]["official"],
        "capital": capitais[0] if capitais else None,
        "regiao": item.get("region"),
        "subregiao": item.get("subregion"),
        "populacao": item.get("population"),
        "area_km2": item.get("area"),
        "moeda": list(moedas.keys())[0] if moedas else None,
        "idioma": list(idiomas.values())[0] if idiomas else None,
    }


def obter_paises():
    """Busca na API e devolve a lista de países já com os campos extraídos."""
    dados = buscar_paises()
    return [extrair_dados_pais(item) for item in dados]


if __name__ == "__main__":
    paises = obter_paises()
    print(f"{len(paises)} países recebidos.")
    if paises:
        print(paises[0])
