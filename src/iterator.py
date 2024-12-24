import time
from ratelimit import limits, sleep_and_retry
import cloudscraper
from bs4 import BeautifulSoup

# Inicializando o scraper
scraper = cloudscraper.create_scraper()

# Definindo o limite de requisições (20 por minuto)
RATE_LIMIT = 20  # Máximo de 20 requisições
TIME_WINDOW = 60  # Em um intervalo de 60 segundos


@sleep_and_retry
@limits(calls=RATE_LIMIT, period=TIME_WINDOW)
def make_request(url):
    """
    Faz uma requisição HTTP para uma URL respeitando o limite de requisições por minuto.
    
    Args:
        url (str): A URL a ser acessada.

    Returns:
        response: O objeto de resposta da requisição.
    """
    response = scraper.get(url)
    response.raise_for_status()
    return response


#### INTERANDO NA LIGA ####

# URL da página principal da liga
url_liga = "https://fbref.com/pt/comps/24/Serie-A-Estatisticas"

# Fazendo a requisição à página principal
response = make_request(url_liga)

# Parsing do HTML retornado
soup = BeautifulSoup(response.text, 'html.parser')

# Selecionando a tabela com informações dos times
table = soup.find('table', {'id': 'results2024241_overall'})

# Dicionário para armazenar os times e suas URLs
teams_links = {}

if table:
    # Itera pelas linhas da tabela de times
    for row in table.find('tbody').find_all('tr'):
        team_cell = row.find('td', {'class': 'left', 'data-stat': 'team'})
        if team_cell:
            # Nome do time
            team_name = team_cell.text.strip()
            # URL do time (relativa)
            team_link = team_cell.find('a')['href']
            # URL completa do time
            full_url = f"https://fbref.com{team_link}"
            # Armazenando no dicionário
            teams_links[team_name] = full_url
else:
    print("Tabela de times não encontrada!")

# Exibindo os times obtidos
print("Times e suas URLs obtidos:")
print(teams_links)


#### INTERANDO NOS TIMES OBTIDOS ####

# Mega dicionário para armazenar informações dos jogadores
players_data = {}

# Itera sobre cada time e sua respectiva URL
for team_name, team_url in teams_links.items():
    print(f"\nAcessando informações do time: {team_name} ({team_url})")
    
    # Fazendo a requisição para a página do time
    response = make_request(team_url)
    
    # Parsing do HTML da página do time
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Localizando a tabela com os jogadores
    players_table = soup.find('table', {'id': 'stats_standard_24'})

    # Lista para armazenar temporariamente os jogadores do time
    team_players = []

    if players_table:
        # Itera pelas linhas da tabela de jogadores
        for row in players_table.find('tbody').find_all('tr'):
            player_cell = row.find('th', {'data-stat': 'player'})
            if player_cell and player_cell.find('a'):
                # Nome do jogador
                player_name = player_cell.find('a').text.strip()
                # URL da estatística do jogador
                player_url = f"https://fbref.com{player_cell.find('a')['href']}"
                
                # Adicionando o jogador ao dicionário principal
                players_data[player_name] = {
                    "clube": team_name,
                    "url": player_url
                }
                # Adicionando à lista temporária do time
                team_players.append({
                    "nome": player_name,
                    "clube": team_name,
                    "url": player_url
                })
    else:
        print(f"Nenhuma tabela de jogadores encontrada para o time {team_name}.")
        continue

    # Debug: Exibindo os 3 primeiros e 3 últimos jogadores do time
    if team_players:
        print("\nPrimeiros 3 jogadores do time:")
        for player in team_players[:3]:
            print(f"Nome: {player['nome']}, Clube: {player['clube']}, URL: {player['url']}")

        print("\nÚltimos 3 jogadores do time:")
        for player in team_players[-3:]:
            print(f"Nome: {player['nome']}, Clube: {player['clube']}, URL: {player['url']}")
    else:
        print(f"Nenhum jogador encontrado para o time {team_name}.")

# Exibindo o mega dicionário completo (opcional)
print("\nInformações completas dos jogadores extraídas:")
for player, data in players_data.items():
    print(f"Jogador: {player}, Clube: {data['clube']}, URL: {data['url']}")
