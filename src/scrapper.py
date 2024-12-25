import requests
import re
import time
from bs4 import BeautifulSoup
import cloudscraper
import pandas as pd
from datetime import datetime
from ratelimit import limits, sleep_and_retry


class PlayerScoutScraper:
    RATE_LIMIT = 9  # Máximo de 15 requisições
    TIME_WINDOW = 60  # Em 60 segundos

    def __init__(self, players_data, db_manager, log_file = "data/log.txt"):
        """
        Inicializa o scraper com o dicionário de jogadores.

        Args:
            players_data (dict): Dicionário contendo as informações dos jogadores e suas URLs.
            db_manager: Gerenciador do banco de dados para salvar os dados dos jogadores.
            log_file (str): Caminho para o arquivo de log.
        """
        self.players_data = players_data
        self.db_manager = db_manager
        self.scraper = cloudscraper.create_scraper()
        self.scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    })
        self.sections = [
            "Estatísticas Padrão",
            "Chutes",
            "Passes",
            "Gols e Criação de Chutes",
            "Defesa",
            "Posse",
            "Estatísticas Variadas"
        ]
        self.log_file = log_file
        with open(self.log_file, "w") as log:
            log.write("Log do Scraper - Jogadores com Falha\n")
            log.write(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def log_failure(self, player_name, error_message):
        """
        Registra uma falha no arquivo de log.

        Args:
            player_name (str): Nome do jogador que falhou.
            error_message (str): Mensagem de erro associada à falha.
        """
        with open(self.log_file, "a") as log:
            log.write(f"Jogador: {player_name} - Erro: {error_message}\n")

    @sleep_and_retry
    @limits(calls=RATE_LIMIT, period=TIME_WINDOW)

    def make_request(self, url):
        """
        Faz uma requisição HTTP para a URL especificada.

        Args:
            url (str): A URL a ser acessada.

        Returns:
            response: O objeto de resposta da requisição.
        """
        time.sleep(1)
        response = self.scraper.get(url)
        response.raise_for_status()
        return response

    def try_url(self, base_url):
        """
        Tenta acessar as páginas do jogador nos formatos `m2` e `m1`.

        Args:
            base_url (str): A URL base do jogador.

        Returns:
            response: O objeto de resposta da requisição.
        """
        for suffix in ["m2", "m1"]:
            url = re.sub(r"m\d", suffix, base_url)
            try:
                return self.make_request(url)
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    continue  # Tentar o próximo formato
                else:
                    raise e
        raise ValueError(f"Ambas as URLs falharam para {base_url}")

    def extract_player_data(self, player_name, player_info):
        """
        Extrai os dados do jogador a partir da página do scout.

        Args:
            player_name (str): Nome do jogador.
            player_info (dict): Informações do jogador, incluindo a URL base.

        Returns:
            DataFrame: DataFrame com as estatísticas do jogador.
        """
        base_url = player_info['scout_url']
        response = self.try_url(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrair dados gerais (nome, clube, posição, etc.)
        meta_div = soup.find('div', {'id': 'meta'})
        if meta_div:
            jogador_id = base_url.split("/")[-4]
            nome_jogador = meta_div.find('h1').text.strip()
            posicao_e_pe = meta_div.find_all('p')[1].text
            posicao = posicao_e_pe.split("Posição:")[1].split("•")[0].strip() if "Posição:" in posicao_e_pe else "Desconhecida"
            pe_favorito = posicao_e_pe.split("Pé favorito:")[1].strip() if "Pé favorito:" in posicao_e_pe else "Desconhecido"

            # Data de nascimento e idade
            data_nascimento_span = meta_div.find('span', {'id': 'necro-birth'})
            if data_nascimento_span and 'data-birth' in data_nascimento_span.attrs:
                data_nascimento_str = data_nascimento_span['data-birth']
                data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
                hoje = datetime.now().date()
                idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            else:
                idade = "Desconhecida"

            # Clube
            clube_strong = meta_div.find('strong', string=lambda text: text and "Clube:" in text)
            if clube_strong:
                clube_p = clube_strong.find_parent('p')
                clube_link = clube_p.find('a') if clube_p else None
                clube = clube_link.text.strip() if clube_link else "Desconhecido"
            else:
                clube = "Desconhecido"

            # Construir a lista de jogadores
            jogadores = []
            jogadores.append({
                "jogador_id": jogador_id,
                "nome_jogador": nome_jogador,
                "clube": clube,
                "idade": idade,
                "posicao": posicao,
                "pe_favorito": pe_favorito
            })
    
            # Passar a lista de jogadores ao gerenciador
            self.db_manager.insert_or_update_jogador(jogadores)
    
        else:
            self.log_failure(player_name, "Meta div não encontrada")
            nome_jogador, posicao, pe_favorito, clube, idade = (
                "Desconhecido", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecida"
            )



        # Extrair estatísticas da tabela principal
        table = soup.find('table', {'id': re.compile(r'^scout_full_')})
        data = []
        if table:
            rows = table.find_all('tr')
            current_section = None

            for row in rows:
                cells = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
                if len(cells) == 1 and cells[0] in self.sections:
                    current_section = cells[0]
                elif len(cells) == 3 and current_section:
                    data.append([current_section] + cells)

            df = pd.DataFrame(data, columns=['Seção', 'Estatística', 'Por 90', 'Percentil'])
            df['Por 90'] = pd.to_numeric(df['Por 90'], errors='coerce')
            df['Percentil'] = pd.to_numeric(df['Percentil'], errors='coerce')
            df.insert(0, 'ID do Jogador', jogador_id)
            df.insert(1, 'Nome do Jogador', nome_jogador)
            df.insert(2, 'Clube', clube)
            df.insert(3, 'Idade', idade)
            df.insert(4, 'Posição', posicao)
            df.insert(5, 'Pé Favorito', pe_favorito)
            df['Data de Extração'] = datetime.now().strftime('%Y-%m-%d')
            df['Posição'] = df['Posição'].str.split('▪').str[0].str.strip()

            # Construir a lista de estatísticas
            estatisticas = []
            for _, row in df.iterrows():
                estatisticas.append({
                    'jogador_id': row['ID do Jogador'],
                    'estatistica': row['Estatística'],
                    'por_90': row['Por 90'],
                    'percentil': row['Percentil']
                })

            # Passar a lista de estatísticas ao gerenciador
            self.db_manager.insert_or_update_estatisticas(estatisticas)

                



            return df
        else:
            print(f"Tabela de estatísticas não encontrada para {player_name}.")
            self.log_failure(player_name, f"Tabela de estatísticas não encontrada para {player_name}.")
            return pd.DataFrame()

    def run(self):
        all_data = []
        for player_name, player_info in self.players_data.items():
            print(f"Processando: {player_name}")
            try:
                #time.sleep(10)  # Pausa entre acessos aos jogadores
                player_df = self.extract_player_data(player_name, player_info)
                #print(player_df['Nome do Jogador', 'ID do Jogador'])
                if not player_df.empty:
                    all_data.append(player_df)
            except Exception as e:
                print(f"Erro ao processar {player_name}: {e}")
                self.log_failure(player_name, str(e))

        self.result_df = pd.concat(all_data, ignore_index=True)
        return self.result_df



