import oracledb
import getpass

from checkpoint5_api_oracle import obter_personagens


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

def criar_tabela():
    """Cria a tabela PERSONAGENS no Oracle."""

    sql = """
        CREATE TABLE personagens (
            id_personagem NUMBER PRIMARY KEY,
            nome VARCHAR2(100) NOT NULL,
            classe VARCHAR2(50),
            raridade NUMBER,
            ataque_max NUMBER,
            vida_max NUMBER,
            atributo VARCHAR2(50),
            poder_total NUMBER,
            categoria_raridade VARCHAR2(30)
        )
    """

    conexao = obter_conexao()

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(sql)
            print("Tabela PERSONAGENS criada com sucesso!")

        except oracledb.Error as erro:
            if "ORA-00955" in str(erro):
                print("Tabela PERSONAGENS já existe!")
            else:
                print(f"Erro ao criar a tabela: {erro}")

        finally:
            conexao.close()
            print("Conexão encerrada.")


def inserir_personagens(personagens):
    """Insere os personagens da API na tabela PERSONAGENS."""

    sql = """
        INSERT INTO personagens (
            id_personagem,
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
            :id_personagem,
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

    conexao = obter_conexao()

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.executemany(sql, personagens)
            conexao.commit()
            print(f"{len(personagens)} personagens inseridos com sucesso!")

        except oracledb.Error as erro:
            conexao.rollback()
            print(f"Erro ao inserir personagens: {erro}")
            print("Alterações desfeitas com rollback.")

        finally:
            conexao.close()
            print("Conexão encerrada.")

# Exibir personagens
def listar_personagens():
    conexao = obter_conexao()

    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM personagens")

            for personagem in cursor:
                print(personagem)

        except oracledb.Error as erro:
            print(f"Erro ao listar: {erro}")

        finally:
            conexao.close()


# UPDATE - Atualizar o nome
def atualizar_personagem(id_personagem, novo_nome):
    conexao = obter_conexao()

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

        finally:
            conexao.close()


# DELETE - Apagar personagem
def excluir_personagem(id_personagem):
    conexao = obter_conexao()

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

        finally:
            conexao.close()

if __name__ == "__main__":
    criar_tabela()
    personagens = obter_personagens()
    if personagens:
    # inserir_personagens(personagens)
        listar_personagens()
    else:
        print("Nenhum personagem recebido na API.")