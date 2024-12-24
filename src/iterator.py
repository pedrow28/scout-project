



import time
from ratelimit import limits, sleep_and_retry
import cloudscraper
from bs4 import BeautifulSoup


class LeagueScraper:
    # Configurações de limite de requisições
    RATE_LIMIT = 17  # Máximo de 10 requisições por minuto
    TIME_WINDOW = 60  # Intervalo de tempo (em segundos)

    def __init__(self, league_url):
        """
        Inicializa o scraper com a URL da liga.
        
        Args:
            league_url (str): URL da página principal da liga.
        """
        self.league_url = league_url
        self.scraper = cloudscraper.create_scraper()
        self.teams_links = {}
        self.players_data = {}

    @sleep_and_retry
    @limits(calls=RATE_LIMIT, period=TIME_WINDOW)
    def make_request(self, url):
        """
        Faz uma requisição HTTP para uma URL respeitando o limite de requisições por minuto.
        
        Args:
            url (str): A URL a ser acessada.

        Returns:
            response: O objeto de resposta da requisição.
        """
        response = self.scraper.get(url)
        response.raise_for_status()
        return response

    def construct_scout_url_m2(self, player_url):
        """
        Constrói a URL da página de scout do jogador com o sufixo m2.

        Args:
            player_url (str): URL da página principal do jogador.

        Returns:
            str: A URL de scout m2 do jogador.
        """
        player_id = player_url.split("/")[-2]
        player_name = player_url.split("/")[-1]
        return f"https://fbref.com/pt/jogadores/{player_id}/scout/365_m2/Relatorio-de-Observacao-de-{player_name}"

    def extract_teams_links(self):
        """
        Extrai os links dos times a partir da página da liga.

        Returns:
            dict: Um dicionário contendo o nome do time como chave e a URL completa como valor.
        """
        print(f"Acessando a página da liga: {self.league_url}")
        response = self.make_request(self.league_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Selecionando a tabela com os times
        table = soup.find('table', {'id': 'results2024241_overall'})

        if table:
            for row in table.find('tbody').find_all('tr'):
                team_cell = row.find('td', {'class': 'left', 'data-stat': 'team'})
                if team_cell:
                    team_name = team_cell.text.strip()
                    team_link = team_cell.find('a')['href']
                    self.teams_links[team_name] = f"https://fbref.com{team_link}"
        else:
            print("Tabela de times não encontrada!")

        print(f"Times encontrados: {len(self.teams_links)}")
        return self.teams_links

    def extract_players_data(self, team_name, team_url):
        """
        Extrai os dados dos jogadores de um time a partir da página do time.
        
        Args:
            team_name (str): Nome do time.
            team_url (str): URL da página do time.

        Returns:
            list: Uma lista de dicionários contendo informações sobre os jogadores.
        """
        print(f"\nAcessando informações do time: {team_name} ({team_url})")
        response = self.make_request(team_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Localizando a tabela de jogadores
        players_table = soup.find('table', {'id': 'stats_standard_24'})
        players = []

        if players_table:
            for row in players_table.find('tbody').find_all('tr'):
                player_cell = row.find('th', {'data-stat': 'player'})
                if player_cell and player_cell.find('a'):
                    player_name = player_cell.find('a').text.strip()
                    player_url = f"https://fbref.com{player_cell.find('a')['href']}"
                    scout_url = self.construct_scout_url_m2(player_url)
                    players.append({
                        "nome": player_name,
                        "clube": team_name,
                        "url": player_url,
                        "scout_url": scout_url
                    })
        else:
            print(f"Nenhuma tabela de jogadores encontrada para o time {team_name}.")

        return players

    def debug_players(self, players, team_name):
        """
        Exibe os 3 primeiros e os 3 últimos jogadores de uma lista para fins de debug.
        
        Args:
            players (list): Lista de dicionários contendo informações dos jogadores.
            team_name (str): Nome do time.
        """
        if players:
            print(f"\nPrimeiros 3 jogadores do time {team_name}:")
            for player in players[:3]:
                print(f"Nome: {player['nome']}, Clube: {player['clube']}, URL: {player['url']}, Scout URL: {player['scout_url']}")

            print(f"\nÚltimos 3 jogadores do time {team_name}:")
            for player in players[-3:]:
                print(f"Nome: {player['nome']}, Clube: {player['clube']}, URL: {player['url']}, Scout URL: {player['scout_url']}")
        else:
            print(f"Nenhum jogador encontrado para o time {team_name}.")

    def run(self):
        """
        Executa o processo completo de scraping para extrair dados da liga e dos jogadores.
        
        Returns:
            dict: O mega dicionário contendo informações de todos os jogadores.
        """
        self.extract_teams_links()
        for team_name, team_url in self.teams_links.items():
            team_players = self.extract_players_data(team_name, team_url)
            self.debug_players(team_players, team_name)
            for player in team_players:
                self.players_data[player["nome"]] = player
                # Adicionar um atraso de segurança
                #time.sleep(5)  # Pausa de 5 segundos entre as requisições

        return self.players_data

