"""
Checkpoint 5 - Versão resumida
Busca os servants da API Atlas Academy (FGO, versão NA), mostra os escolhidos
no menu e salva no Oracle somente esses personagens.
"""

import getpass
import random

import oracledb
import requests

URL = "https://api.atlasacademy.io/export/NA/basic_servant.json"
DSN = "oracle.fiap.com.br:1521/orcl"


# ---------- API ----------
def definir_categoria(raridade):
    if raridade <= 3:
        return "Comum"
    if raridade == 4:
        return "Raro"
    return "Ultra raro"


def buscar_personagens():
    """Faz o GET na API e devolve a lista de personagens (vazia se der erro)."""
    try:
        resposta = requests.get(URL, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.exceptions.RequestException, ValueError) as erro:
        print(f"Erro ao acessar a API: {erro}")
        return []

    personagens = []
    for item in dados:
        # collectionNo = 0 são inimigos/NPCs
        if not isinstance(item, dict) or not item.get("collectionNo"):
            continue
        ataque = item.get("atkMax") or 0
        vida = item.get("hpMax") or 0
        raridade = item.get("rarity") or 0
        personagens.append({
            "id_personagem": item["collectionNo"],
            "nome": item.get("name"),
            "classe": item.get("className"),
            "raridade": raridade,
            "ataque_max": ataque,
            "vida_max": vida,
            "atributo": item.get("attribute"),
            "poder_total": ataque + vida,
            "categoria_raridade": definir_categoria(raridade),
        })
    return sorted(personagens, key=lambda p: p["id_personagem"])


# ---------- BANCO ----------
def criar_tabela(conexao):
    sql = """
        CREATE TABLE personagens (
            id_personagem INTEGER PRIMARY KEY,
            nome VARCHAR2(100) NOT NULL,
            classe VARCHAR2(50) NOT NULL,
            raridade NUMBER NOT NULL,
            ataque_max NUMBER NOT NULL,
            vida_max NUMBER NOT NULL,
            atributo VARCHAR2(50),
            poder_total NUMBER NOT NULL,
            categoria_raridade VARCHAR2(30) NOT NULL
        )
    """
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
        print("Tabela PERSONAGENS criada.")
    except oracledb.Error as erro:
        if "ORA-00955" not in str(erro):  # já existe
            print(f"Erro ao criar a tabela: {erro}")


def salvar_personagens(conexao, personagens):
    """Insere os personagens escolhidos, ignorando os que já estão salvos."""
    sql = """
        MERGE INTO personagens p
        USING (SELECT :id_personagem AS id FROM dual) s
        ON (p.id_personagem = s.id)
        WHEN NOT MATCHED THEN INSERT (
            id_personagem, nome, classe, raridade, ataque_max,
            vida_max, atributo, poder_total, categoria_raridade
        ) VALUES (
            :id_personagem, :nome, :classe, :raridade, :ataque_max,
            :vida_max, :atributo, :poder_total, :categoria_raridade
        )
    """
    try:
        with conexao.cursor() as cursor:
            cursor.executemany(sql, personagens)
            novos = cursor.rowcount
        conexao.commit()
        print(f"{novos} novo(s) salvo(s) no banco "
              f"({len(personagens) - novos} já existiam).")
    except oracledb.Error as erro:
        conexao.rollback()
        print(f"Erro ao salvar no banco: {erro} (rollback feito)")


def listar_salvos(conexao):
    """Devolve os personagens salvos no banco (lista vazia se não houver ou der erro)."""
    sql = """
        SELECT id_personagem, nome, classe, raridade, poder_total, categoria_raridade
        FROM personagens
        ORDER BY id_personagem
    """
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
            colunas = [c[0].lower() for c in cursor.description]
            return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except oracledb.Error as erro:
        print(f"Erro ao listar: {erro}")
        return []


def excluir_personagem(conexao, id_personagem):
    """Exclui um personagem pelo id. Devolve quantas linhas foram apagadas."""
    try:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM personagens WHERE id_personagem = :id",
                           {"id": id_personagem})
            apagados = cursor.rowcount
        conexao.commit()
        return apagados
    except oracledb.Error as erro:
        conexao.rollback()
        print(f"Erro ao excluir: {erro} (rollback feito)")
        return 0


# ---------- MENU ----------
def imprimir(p):
    print(f"\nId: {p['id_personagem']}\nNome: {p['nome']}\nClasse: {p['classe']}"
          f"\nRaridade: {p['raridade']}\nAtaque Máximo: {p['ataque_max']}"
          f"\nVida Máxima: {p['vida_max']}\nAtributo: {p['atributo']}"
          f"\nPoder Total: {p['poder_total']}"
          f"\nCategoria por Raridade: {p['categoria_raridade']}")


def mostrar_e_salvar(conexao, escolhidos):
    for p in escolhidos:
        imprimir(p)
    print()
    salvar_personagens(conexao, escolhidos)


def ler_int(texto):
    try:
        return int(input(texto))
    except ValueError:
        print("\nDigite apenas números inteiros.\n")
        return None


def escolha_indice(conexao, lista):
    i = ler_int(f"Índice desejado (1 - {len(lista)}): ")
    if i is None:
        return
    if 1 <= i <= len(lista):
        mostrar_e_salvar(conexao, [lista[i - 1]])
    else:
        print("\nÍndice inválido.\n")


def escolha_intervalo(conexao, lista):
    ini = ler_int("Índice inicial: ")
    fim = ler_int("Índice final: ")
    if ini is None or fim is None:
        return
    if 1 <= ini <= fim <= len(lista):
        mostrar_e_salvar(conexao, lista[ini - 1:fim])
    else:
        print(f"\nIntervalo inválido (use 1 - {len(lista)}, inicial <= final).\n")


def escolha_aleatoria(conexao, lista):
    mostrar_e_salvar(conexao, random.sample(lista, min(5, len(lista))))


def ver_salvos(conexao):
    salvos = listar_salvos(conexao)
    if not salvos:
        print("\nNenhum personagem salvo.\n")
        return salvos
    print(f"\n{len(salvos)} personagem(ns) salvo(s):\n")
    for p in salvos:
        print(f"{p['id_personagem']:>4} - {p['nome']} | {p['classe']} | "
              f"raridade {p['raridade']} ({p['categoria_raridade']}) | "
              f"poder {p['poder_total']}")
    print()
    return salvos


def excluir_salvo(conexao):
    salvos = ver_salvos(conexao)
    if not salvos:
        return
    id_escolhido = ler_int("Id do personagem a excluir (0 cancela): ")
    if id_escolhido is None or id_escolhido == 0:
        return
    alvo = next((p for p in salvos if p["id_personagem"] == id_escolhido), None)
    if alvo is None:
        print("\nId não encontrado entre os personagens salvos.\n")
        return
    confirmacao = input(f"Excluir {alvo['nome']}? (y/n): ").lower()
    if confirmacao == "y":
        if excluir_personagem(conexao, id_escolhido):
            print("\nPersonagem excluído!\n")
    elif confirmacao == "n":
        print("\nVoltando...\n")
    else:
        print("\nEscolha inválida.\n")


def main():
    lista = buscar_personagens()
    if not lista:
        return

    usuario = input("Usuário Oracle: ")
    senha = getpass.getpass("Senha Oracle: ")
    try:
        conexao = oracledb.connect(user=usuario, password=senha, dsn=DSN)
    except oracledb.Error as erro:
        print(f"Erro ao conectar ao Oracle: {erro}")
        return

    try:
        criar_tabela(conexao)
        print(f"\n{len(lista)} personagens carregados da API.")
        while True:
            print("\n==============================")
            print("1 - Escolha por índice\n2 - Escolha por intervalo\n"
                  "3 - 5 escolhas aleatórias\n4 - Ver personagens salvos\n"
                  "5 - Excluir personagem salvo\n0 - Sair")
            print("==============================")
            escolha = ler_int("Escolha uma ação: ")
            if escolha == 0:
                break
            elif escolha == 1:
                escolha_indice(conexao, lista)
            elif escolha == 2:
                escolha_intervalo(conexao, lista)
            elif escolha == 3:
                escolha_aleatoria(conexao, lista)
            elif escolha == 4:
                ver_salvos(conexao)
            elif escolha == 5:
                excluir_salvo(conexao)
            elif escolha is not None:
                print("\nEscolha inválida.\n")
    finally:
        conexao.close()


main()