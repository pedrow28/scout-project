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
            "Standard Stats",
            "Shooting",
            "Passing",
            "Pass Types",
            "Goal and Shot Creation",
            "Defense",
            "Possession",
            "Miscellaneous Stats"
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
            player_id = base_url.split("/")[-4]
            # Nome do jogador
    # Nome do jogador
            name = meta_div.find('h1').text.strip()

            # Posição e pé dominante
            position_tag_corrected = meta_div.find('strong', string=lambda x: x and 'Position:' in x)
            if position_tag_corrected:
                position_full_text_corrected = position_tag_corrected.parent.get_text(" ", strip=True)
                position = position_full_text_corrected.split("▪")[0].replace("Position:", "").strip()
                foot = position_full_text_corrected.split("▪")[1].replace("Footed:", "").strip() if "▪" in position_full_text_corrected else "Desconhecido"
            else:
                position = "Desconhecida"
                foot = "Desconhecido"

            # Clube atual
            club_tag_corrected = meta_div.find('strong', string=lambda x: x and 'Club:' in x)
            team = club_tag_corrected.find_next_sibling('a').text.strip() if club_tag_corrected and club_tag_corrected.find_next_sibling('a') else "Clube Desconhecido"

            # Data de nascimento e idade
            birth_info = meta_div.find('span', {'id': 'necro-birth'})
            if birth_info:
                birth_date = birth_info['data-birth']
                birth_date_formatted = datetime.strptime(birth_date, "%Y-%m-%d").date()
                hoje = datetime.now().date()
                age = hoje.year - birth_date_formatted.year - (
                    (hoje.month, hoje.day) < (birth_date_formatted.month, birth_date_formatted.day)
                )
            else:
                birth_date = "Desconhecida"
                age = "Desconhecida"


            print(f"ID: {player_id}, Jogador: {name}, Time: {team}, Idade: {age}, Posição: {position}, Pé: {foot}")


            # Construir a lista de jogadores
            players = []
            players.append({
                "player_id": player_id,
                "name": name,
                "team": team,
                "age": age,
                "position": position,
                "foot": foot
            })
    
            # Passar a lista de jogadores ao gerenciador
            self.db_manager.insert_or_update_players(players)
    
        else:
            self.log_failure(player_name, "Meta div não encontrada")
            name, team, age, position, foot = (
                "Desconhecido", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecido", "Desconhecido"
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

            df = pd.DataFrame(data, columns=['session', 'stat', 'per_90_minutes', 'percentil'])
            df['per_90_minutes'] = pd.to_numeric(df['per_90_minutes'], errors='coerce')
            df['percentil'] = pd.to_numeric(df['percentil'], errors='coerce')
            df.insert(0, 'id', player_id)
            df.insert(1, 'name', name)
            df.insert(2, 'team', team)
            df.insert(3, 'age', age)
            df.insert(4, 'position', position)
            df.insert(5, 'foot', foot)
            df['Data de Extração'] = datetime.now().strftime('%Y-%m-%d')
            #df['Posição'] = df['Posição'].str.split('▪').str[0].str.strip()

            # Construir a lista de estatísticas
            statistics = []
            for _, row in df.iterrows():
                statistics.append({
                    'player_id': row['id'],
                    'stat': row['stat'],
                    'per_90_minutes': row['per_90_minutes'],
                    'percentil': row['percentil']
                })

            # Passar a lista de estatísticas ao gerenciador
            self.db_manager.insert_or_update_statistics(statistics)

                



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



