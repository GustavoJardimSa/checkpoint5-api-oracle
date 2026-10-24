import time

import requests

BASE_URL = "https://restcountries.com/v3.1"
CAMPOS = "cca3,name,capital,region,subregion,population,area,currencies,languages"
TIMEOUT_SEGUNDOS = 10
MAX_TENTATIVAS = 3


class ErroAPI(Exception):
    """Erro de negócio levantado quando a API não pôde ser consumida."""


def _requisitar(url, params=None):
    """Faz o GET com tratamento de erros de conexão e de status HTTP."""
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = requests.get(url, params=params, timeout=TIMEOUT_SEGUNDOS)
        except requests.exceptions.Timeout:
            print(f"[AVISO] Timeout (tentativa {tentativa}/{MAX_TENTATIVAS}).")
        except requests.exceptions.ConnectionError:
            print(f"[AVISO] Falha de conexão (tentativa {tentativa}/{MAX_TENTATIVAS}).")
        except requests.exceptions.RequestException as erro:
            raise ErroAPI(f"Erro inesperado na requisição: {erro}") from erro
        else:
            if resposta.status_code == 200:
                return resposta
            if resposta.status_code == 404:
                raise ErroAPI("404 - Recurso não encontrado (verifique a URL ou a região).")
            if resposta.status_code >= 500:
                print(f"[AVISO] Erro {resposta.status_code} no servidor "
                      f"(tentativa {tentativa}/{MAX_TENTATIVAS}).")
            else:
                raise ErroAPI(f"Erro HTTP {resposta.status_code}: {resposta.text[:200]}")

        if tentativa < MAX_TENTATIVAS:
            time.sleep(2 * tentativa)  # espera um pouco mais a cada tentativa

    raise ErroAPI("API indisponível após várias tentativas.")


def _extrair_registro(item):
    """Converte o JSON aninhado de um país em um dicionário simples (plano)."""
    moedas = item.get("currencies") or {}
    idiomas = item.get("languages") or {}
    capitais = item.get("capital") or []

    # Pega só a primeira moeda: {"BRL": {"name": "Brazilian real", ...}}
    codigo_moeda = next(iter(moedas), None)

    return {
        "codigo_pais": item.get("cca3"),
        "nome_comum": (item.get("name") or {}).get("common"),
        "nome_oficial": (item.get("name") or {}).get("official"),
        "capital": capitais[0] if capitais else None,
        "regiao": item.get("region"),
        "subregiao": item.get("subregion"),
        "populacao": item.get("population"),
        "area_km2": item.get("area"),
        "moeda": codigo_moeda,
        "idioma": next(iter(idiomas.values()), None),
    }


def buscar_paises(regiao=None):
    """
    Busca países na API e devolve uma lista de dicionários simples.

    regiao: opcional (africa, americas, asia, europe, oceania).
    Levanta ErroAPI se algo der errado.
    """
    if regiao:
        url = f"{BASE_URL}/region/{regiao}"
    else:
        url = f"{BASE_URL}/all"

    resposta = _requisitar(url, params={"fields": CAMPOS})

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise ErroAPI("A API retornou um JSON inválido.") from erro

    if not isinstance(dados, list) or not dados:
        raise ErroAPI("A API retornou uma resposta vazia ou em formato inesperado.")

    registros = [_extrair_registro(item) for item in dados]
    # Garante que todo registro tem a chave primária (cca3)
    return [r for r in registros if r["codigo_pais"]]


if __name__ == "__main__":
    # Teste rápido: python api_client.py
    try:
        lista = buscar_paises("americas")
        print(f"{len(lista)} países recebidos. Exemplo:")
        print(lista[0])
    except ErroAPI as e:
        print(f"[ERRO] {e}")