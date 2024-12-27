"""

Constrói a base de dados de jogadores a partir de scouts da liga selecionada e
exporta para a base geral.


"""

from src.iterator import LeagueScraper
from src.scrapper import PlayerScoutScraper
from src.dbmanager import DatabaseManager
import time
from ratelimit import limits, sleep_and_retry





ligas = [
    {"liga": "Serie A", "url": "https://fbref.com/pt/comps/24/Serie-A-Estatisticas"}
    {"liga": "Liga Profesional de Fútbol Argentina", "url": "https://fbref.com/pt/comps/21/Liga-Profesional-Argentina-Estatisticas"},
    {"liga": "Chilean Primera División", "url": "https://fbref.com/pt/comps/35/Primera-Division-Estatisticas"},
    {"liga": "Categoría Primera A", "url": "https://fbref.com/pt/comps/41/Primera-A-Estatisticas"},
    {"liga": "Liga Profesional Ecuador", "url": "https://fbref.com/pt/comps/58/Serie-A-Estatisticas"},
    {"liga": "Liga MX", "url": "https://fbref.com/pt/comps/31/Liga-MX-Estatisticas"},
    {"liga": "Paraguayan Primera División", "url": "https://fbref.com/pt/comps/61/Primeira-Division-Estatisticas"},
    {"liga": "Liga 1 de Fútbol Profesional", "url": "https://fbref.com/pt/comps/44/Liga-1-Estatisticas"},
    {"liga": "Primeira Liga", "url": "https://fbref.com/pt/comps/32/Primeira-Liga-Estatisticas"},
    {"liga": "South African Premier Division", "url": "https://fbref.com/pt/comps/52/Premier-Division-Estatisticas"},
    {"liga": "Uruguayan Primera División", "url": "https://fbref.com/pt/comps/45/Uruguayan-Primera-Division-Estatisticas"},
    {"liga": "Major League Soccer", "url": "https://fbref.com/pt/comps/22/Major-League-Soccer-Estatisticas"},
    {"liga": "Venezuelan Primera División", "url": "https://fbref.com/pt/comps/105/Venezuelan-Primera-Division-Estatisticas"},
    {"liga": "Campeonato Brasileiro Série B", "url": "https://fbref.com/pt/comps/38/Serie-B-Estatisticas"}
]


def main(url):
    # Inicializar o gerenciador do banco de dados
    """
    Constrói a base de dados de jogadores a partir de scouts da liga selecionada.
    
    1. Cria o scraper para a liga e extrai o dicionário de URLs dos times.
    2. Cria o scraper para os scouts dos jogadores e extrai o DataFrame consolidado.
    3. Salva as informações no banco de dados.
    
    Returns:
        None
    """
    db_manager = DatabaseManager("data/jogadores.db")
    # 1. Criar o scraper para a liga (gera o dicionário de URLs dos times)
    league_url = url
    league_scraper = LeagueScraper(league_url)
    teams_data = league_scraper.run()  # Retorna o dicionário de times e suas URLs
    from ratelimit import limits, sleep_and_retry

    @sleep_and_retry
    @limits(calls=1, period=60)
    def rate_limited_request():
        return league_scraper.run()

    teams_data = rate_limited_request()  # Retorna o dicionário de times e suas URLs
    print(f"URLs dos times extraídas: {teams_data}")
    time.sleep(30)  # Espera 60 segundos para evitar bloqueio

    # 2. Criar o scraper para os scouts dos jogadores
    player_scraper = PlayerScoutScraper(teams_data, db_manager)
    scout_data = player_scraper.run()  # Retorna o DataFrame consolidado
    print(scout_data.head())  # Exibe as primeiras linhas para verificação

    # Fechar a conexão com o banco de dados
    db_manager.close()
    print("Processo concluído. Dados salvos no banco de dados.")

@sleep_and_retry
@limits(calls=1, period=10)
def process_league(liga):
    print(f"Processando liga: {liga['liga']}")
    main(liga['url'])

def process_all_leagues(leagues):
    for liga in leagues:
        process_league(liga)

if __name__ == "__main__":
    process_all_leagues(ligas)
