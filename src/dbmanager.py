import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        """
        Inicializa o gerenciador do banco de dados e cria as tabelas necessárias.

        Args:
            db_path (str): Caminho para o arquivo do banco de dados.
        """
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """
        Cria as tabelas de jogadores e estatísticas no banco de dados.
        """
        # Tabela de Jogadores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogadores (
                id TEXT PRIMARY KEY,
                nome TEXT,
                time TEXT,
                idade INTEGER,
                posição TEXT,
                pé_preferido TEXT
            )
        """)

        # Tabela de Estatísticas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatisticas (
                jogador_id TEXT,
                estatistica TEXT,
                por_90 REAL,
                percentil REAL,
                PRIMARY KEY (jogador_id, estatistica),
                FOREIGN KEY (jogador_id) REFERENCES jogadores(id) ON DELETE CASCADE ON UPDATE NO ACTION
            )
        """)

        self.connection.commit()

    def insert_or_update_jogador(self, jogador):
        """
        Insere ou atualiza as informações de um jogador no banco.

        Args:
            jogador (dict): Dados do jogador, incluindo id, nome, time, idade, posição e pé_preferido.
        """
        self.cursor.execute("""
            INSERT INTO jogadores (id, nome, time, idade, posição, pé_preferido)
            VALUES (:id, :nome, :time, :idade, :posição, :pé_preferido)
            ON CONFLICT(id) DO UPDATE SET
                nome = excluded.nome,
                time = excluded.time,
                idade = excluded.idade,
                posição = excluded.posição,
                pé_preferido = excluded.pé_preferido
        """, jogador)
        self.connection.commit()

    def insert_or_update_estatisticas(self, jogador_id, estatisticas):
        """
        Insere ou atualiza as estatísticas de um jogador no banco.

        Args:
            jogador_id (str): ID do jogador.
            estatisticas (list of dict): Lista de estatísticas do jogador.
        """
        for estatistica in estatisticas:
            self.cursor.execute("""
                INSERT INTO estatisticas (jogador_id, estatistica, por_90, percentil)
                VALUES (:jogador_id, :estatistica, :por_90, :percentil)
                ON CONFLICT(jogador_id, estatistica) DO UPDATE SET
                    por_90 = excluded.por_90,
                    percentil = excluded.percentil
            """, {
                'jogador_id': jogador_id,
                'estatistica': estatistica['estatistica'],
                'por_90': estatistica.get('por_90'),
                'percentil': estatistica.get('percentil')
            })
        self.connection.commit()

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.connection.close()
