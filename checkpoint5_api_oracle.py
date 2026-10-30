"""
Checkpoint 5 - Parte A: Consumo de API Pública (requests)
API: Atlas Academy API (https://api.atlasacademy.io) - dados de Fate/Grand Order
Dados usados: apenas os personagens (servants) da versão NA do jogo.
"""

import requests
import random
import oracledb



# SEÇÃO API
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
    if (raridade >= 0 and raridade <= 3):
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





# SEÇÃO BANCO DE DADOS
DB_USER = input("Digite seu usuário Oracle: ")
DB_PASS = input("Digite sua senha Oracle: ")
DB_DSN = "oracle.fiap.com.br:1521/orcl"

def obter_conexao():
    try:
        conexao = oracledb.connect(
            user=DB_USER,
            password=DB_PASS,
            dsn=DB_DSN
        )

        print("Conexão com o Oracle realizada com sucesso!")
        return conexao

    except oracledb.Error as erro:
        print(f"Erro ao conectar ao Oracle: {erro}")
        return None

def criar_tabela(conexao):
    """Cria a tabela PERSONAGENS no Oracle."""

    sql = """
        CREATE TABLE personagens (
            id_personagem INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nome VARCHAR2(100) NOT NULL,
            classe VARCHAR2(50) NOT NULL,
            raridade NUMBER NOT NULL,
            ataque_max NUMBER NOT NULL,
            vida_max NUMBER NOT NULL,
            atributo VARCHAR2(50) NOT NULL,
            poder_total NUMBER NOT NULL,
            categoria_raridade VARCHAR2(30) NOT NULL
        )
    """

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(sql)
            print("Tabela PERSONAGENS criada com sucesso!\n")

        except oracledb.Error as erro:
            if "ORA-00955" in str(erro):
                print("Tabela PERSONAGENS já existe!\n")
            else:
                print(f"Erro ao criar a tabela: {erro}\n")

def inserir_personagens(personagem, conexao):
    """Insere os personagens da API na tabela PERSONAGENS."""

    sql = """
        INSERT INTO personagens (
            nome,
            classe,
            raridade,
            ataque_max,
            vida_max,
            atributo,
            poder_total,
            categoria_raridade
        )
        VALUES (
            :nome,
            :classe,
            :raridade,
            :ataque_max,
            :vida_max,
            :atributo,
            :poder_total,
            :categoria_raridade
        )
    """

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(sql, personagem)
            conexao.commit()
            print(f"o personagem foi inserido com sucesso!")

        except oracledb.Error as erro:
            conexao.rollback()
            print(f"Erro ao inserir o personagem: {erro}")
            print("Alterações desfeitas com rollback.")

def listar_personagens(conexao):

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM personagens ORDER BY id_personagem")
            resultado = cursor.fetchall()

            listaPersonagens = []
            for personagem in resultado:
                listaPersonagens.append({
                "id_personagem": personagem[0],
                "nome": personagem[1],
                "classe": personagem[2],
                "raridade": personagem[3],
                "ataque_max": personagem[4],
                "vida_max": personagem[5],
                "atributo": personagem[6],
                "poder_total": personagem[7],
                "categoria_raridade": personagem[8]
            })
            return listaPersonagens
        except oracledb.Error as erro:
            print(f"Erro ao listar: {erro}")
            return []

def atualizar_personagem(id_personagem, novo_nome, conexao):

    if conexao:
        try:
            cursor = conexao.cursor()

            cursor.execute(
                """
                UPDATE personagens
                SET nome = :nome
                WHERE id_personagem = :id
                """,
                {"nome": novo_nome, "id": id_personagem}
            )

            conexao.commit()
            print("Personagem atualizado!")

        except oracledb.Error as erro:
            conexao.rollback()
            print(f"Erro ao atualizar: {erro}")

def excluir_personagem(id_personagem, conexao):

    if conexao:
        try:
            cursor = conexao.cursor()

            cursor.execute(
                """
                DELETE FROM personagens
                WHERE id_personagem = :id
                """,
                {"id": id_personagem}
            )

            conexao.commit()
            print("Personagem excluído!")

        except oracledb.Error as erro:
            conexao.rollback()
            print(f"Erro ao excluir: {erro}")

def contarPersonagensBD(conexao):
    if conexao:
        try:
            cursor = conexao.cursor()
            qtdPersonagens = cursor.execute("SELECT COUNT(*) FROM personagens").fetchone()[0]
            print(f'{qtdPersonagens} personagens personalizados.')
            return qtdPersonagens
        except oracledb.Error as erro:
            print(f"Erro na contagem de personagens personalizados: {erro}")
            return 0
            





# SEÇÃO AÇÕES E INTERFACE
def imprimirDados(item):
    print(f'\nId: {item["id_personagem"]}\nNome: {item["nome"]}\nClasse: {item["classe"]}\nRaridade: {item["raridade"]}\nAtaque Maximo: {item["ataque_max"]}\nVida Maxima: {item["vida_max"]}\nAtributo: {item["atributo"]}\nPoder Total: {item["poder_total"]}\nCategoria por Raridade: {item["categoria_raridade"]}\n')

def escolhaIndice(listaAPI, conexao):
    qtdPersonagensBD = contarPersonagensBD(conexao)
    if qtdPersonagensBD:
        listaBD = listar_personagens(conexao)
        listaCompleta = listaAPI + listaBD
        print(f'\n\nindices:\n1 - {len(listaAPI)}: personagens originais\n{len(listaAPI) + 1} - {len(listaCompleta)} personagens personalizados\n\n')
    else:
        listaCompleta = listaAPI
        print(f'\n\nindices:\n1 - {len(listaCompleta)}\n\n')
    try:
        indice = int(input(f'digite o indice desejado (1 - {len(listaCompleta)}): '))
    except ValueError:
        print('\nDigite apenas numeros inteiros\n')
    else:
        if(indice >= 1 and indice <= (len(listaCompleta))):
            imprimirDados(listaCompleta[indice - 1])
        else:
            print('\nindice inválido\n')

def escolhaIntervalo(listaAPI, conexao):
    qtdPersonagensBD = contarPersonagensBD(conexao)
    if qtdPersonagensBD:
        listaBD = listar_personagens(conexao)
        listaCompleta = listaAPI + listaBD
        print(f'\n\nindices:\n1 - {len(listaAPI)}: personagens originais\n{len(listaAPI) + 1} - {len(listaCompleta)} personagens personalizados\n\n')
    else:
        listaCompleta = listaAPI
        print(f'\n\nindices:\n1 - {len(listaCompleta)}\n\n')
    try:
        indiceInicial = int(input('Escolha o indice inicial: '))
        indiceFinal = int(input('Escolha o indice final: '))
    except ValueError:
        print('\nDigite apenas numeros inteiros\n')
    else:
        if(indiceInicial < 1):
            print('\no indice inicial não pode ser menor que 1\n')
        elif(indiceInicial > indiceFinal):
            print('\nEscolha inválida, o indice inicial deve ser menor que o final\n')
        elif(indiceInicial == indiceFinal):
            print('\nEscolha inválida, os dois indices não podem ser iguais\n')
        elif(indiceInicial > len(listaCompleta) or indiceFinal > len(listaCompleta)):
            print('\nO indice não pode ser maior que a lista\n')
        else:
            for i in range((indiceInicial - 1), (indiceFinal)):
                imprimirDados(listaCompleta[i])

def escolhaAleatória(listaAPI, conexao):
    qtdPersonagensBD = contarPersonagensBD(conexao)
    if qtdPersonagensBD:
        listaBD = listar_personagens(conexao)
        listaCompleta = listaAPI + listaBD
        print(f'\n\nindices:\n1 - {len(listaAPI)}: personagens originais\n{len(listaAPI) + 1} - {len(listaCompleta)} personagens personalizados\n\n')
    else:
        listaCompleta = listaAPI
        print(f'\n\nindices:\n1 - {len(listaCompleta)}\n\n')
    indicesSorteados = random.sample(range(len(listaCompleta)), 5)
    for i in indicesSorteados:
        imprimirDados(listaCompleta[i])


def opcoesPersonalizacao(listaAPI, conexao):
    while True:
        print('==============================')
        print('Ações Personalizadas:\n1 - Criar Tabela\n2 - Criar personagem com dados escolhidos\n3 - Criar personagem com dados aleatorios\n4 - Trocar nome de personagem\n5 - Excluir personagem\n0 - Voltar')
        print('==============================')
        try:
            escolha = int(input('Escolha uma Ação: '))
        except ValueError:
            print('\nDigite apenas numeros inteiros\n')
        else:
            if(escolha == 0):
                return
            elif(escolha == 1):
                criar_tabela(conexao)
            elif(escolha == 2):
                criarPersonagem(1, listaAPI, conexao)
            elif(escolha == 3):
                criarPersonagem(2, listaAPI, conexao)
            elif(escolha == 4):
                atualizarNomePersonagem(conexao)
            elif(escolha == 5):
                apagarPersonagem(conexao)
            else:
                print('\nEscolha inválida\n')

def escolhaDados(tipoCriacao, dados, listaAPI):
    dadoAtual = dados[0]
    nomeDado = ''
    match dadoAtual:
        case 0:
            nomeDado = "classe"
        case 1:
            nomeDado = "raridade"
        case 2:
            nomeDado = "ataque_max"
        case 3:
            nomeDado = "vida_max"
        case 4:
            nomeDado = "atributo"
    if tipoCriacao == 1:
        while True:
            try:
                indice = int(input(f'digite o indice do personagem que deseja pegar o dado {nomeDado}: '))
            except ValueError:
                print('\nDigite apenas numeros inteiros\n')
            else:
                if (indice >= 1 and indice <= len(listaAPI)):
                    personagemDado = listaAPI[indice - 1]
                    dadoPersonagem = personagemDado[nomeDado]
                    print(f'\nDado escolhido: {dadoPersonagem}\n')
                    confirmacao = input('Confirme sua escolha (y/n): ').lower()
                    if (confirmacao == 'y'):
                        dados.append(dadoPersonagem)
                        dados[0] += 1
                        return dados
                    elif (confirmacao == 'n'):
                        print('Voltando...')
                    else:
                        print('Escolha inválida')
                else:
                    print('Indice invalido')
    elif tipoCriacao == 2:
        indice = random.randint(0, len(listaAPI) - 1)
        dados.append(listaAPI[indice][nomeDado])
        dados[0] += 1
        return dados


def criarPersonagem(modo, listaAPI, conexao):
    nome = input('Digite o nome do personagem: ')
    dados = [0, nome]
    while len(dados) < 7:
        dados = escolhaDados(modo, dados, listaAPI)

    ataque_max = dados[4]
    vida_max = dados[5]
    raridade = dados[3]

    personagem = {
        "nome": dados[1],
        "classe": dados[2],
        "raridade": raridade,
        "ataque_max": ataque_max,
        "vida_max": vida_max,
        "atributo": dados[6],
        "poder_total": ataque_max + vida_max,
        "categoria_raridade": definirCategoria(raridade)
    }
    inserir_personagens(personagem, conexao)

def atualizarNomePersonagem(conexao):
    qtdPersonagensBD = contarPersonagensBD(conexao)
    if qtdPersonagensBD > 0:
        listaBD = listar_personagens(conexao)
        try:
            print(f'\nQuantidade de Personagens personalizados: {qtdPersonagensBD}')
            indice = int(input('Digite o indice do personagem que deseja mudar o nome: '))
        except ValueError:
            print('\nDigite apenas numeros inteiros\n')
        else:
            if (indice >= 1 and indice <= len(listaBD)):
                personagem = listaBD[indice - 1]
                print(f'\npersonagem escolhido: {personagem["nome"]}')
                confirmacao = input('Confirme sua escolha (y/n): ').lower()
                if (confirmacao == 'y'):
                    nome = input('Digite o novo nome: ')
                    atualizar_personagem(personagem["id_personagem"], nome, conexao)
                elif (confirmacao == 'n'):
                    print('\nVoltando...\n')
                else:
                    print('\nEscolha inválida\n')
            else:
                print('\nIndice Invalido\n')
    else:
        print('\nNenhum personagem criado.\n')

def apagarPersonagem(conexao):
    qtdPersonagensBD = contarPersonagensBD(conexao)
    if qtdPersonagensBD > 0:
        listaBD = listar_personagens(conexao)
        try:
            print(f'\nQuantidade de Personagens personalizados: {qtdPersonagensBD}')
            indice = int(input('Digite o indice do personagem que deseja apagar:'))
        except ValueError:
            print('\nDigite apenas numeros inteiros\n')
        else:
            if (indice >= 1 and indice <= len(listaBD)):
                personagem = listaBD[indice - 1]
                print(f'personagem escolhido: {personagem["nome"]}')
                confirmacao = input('\nConfirme sua escolha (y/n): ').lower()
                if (confirmacao == 'y'):
                    excluir_personagem(personagem["id_personagem"], conexao)
                elif (confirmacao == 'n'):
                    print('\nVoltando...\n')
                else:
                    print('\nEscolha inválida\n')
            else:
                print('\nIndice Invalido\n')
    else:
        print('\nNenhum personagem criado.\n')




#MAIN
def main():
    listaAPI = obter_personagens()
    if listaAPI:
        conexao = obter_conexao()
        if conexao:
            print(f"\n{len(listaAPI)} personagens originais.\n")
            while True:
                print('==============================')
                print('Ações:\n1 - Escolha por indice\n2 - Escolha por intervalo\n3 - 5 escolhas aleatórias\n4 - Opções de personalização\n0 - Sair')
                print('==============================')
                try:
                    escolha = int(input('Escolha uma Ação: '))
                except ValueError:
                    print('\nDigite apenas numeros inteiros\n')
                else:
                    if(escolha == 0):
                        conexao.close()
                        break
                    elif(escolha == 1):
                        escolhaIndice(listaAPI, conexao)
                    elif(escolha == 2):
                        escolhaIntervalo(listaAPI, conexao)
                    elif(escolha == 3):
                        escolhaAleatória(listaAPI, conexao)
                    elif(escolha == 4):
                        opcoesPersonalizacao(listaAPI, conexao)
                    else:
                        print('\nEscolha inválida\n')

                

main()