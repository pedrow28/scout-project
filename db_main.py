"""

Constrói a base de dados de jogadores a partir de scouts da liga selecionada e
exporta para a base geral.


"""

from src.iterator import LeagueScraper
from src.scrapper import PlayerScoutScraper
from src.dbmanager import DatabaseManager
import time

def main():
    # Inicializar o gerenciador do banco de dados
    db_manager = DatabaseManager("data/jogadores.db")
    # 1. Criar o scraper para a liga (gera o dicionário de URLs dos times)
    league_url = "https://fbref.com/pt/comps/24/Serie-A-Estatisticas"
    league_scraper = LeagueScraper(league_url)
    teams_data = league_scraper.run()  # Retorna o dicionário de times e suas URLs
    print(f"URLs dos times extraídas: {teams_data}")
    time.sleep(60)  # Espera 5 segundos para evitar bloqueio

    # 2. Criar o scraper para os scouts dos jogadores
    player_scraper = PlayerScoutScraper(teams_data, db_manager)
    scout_data = player_scraper.run()  # Retorna o DataFrame consolidado
    print(scout_data.head())  # Exibe as primeiras linhas para verificação

    # Fechar a conexão com o banco de dados
    db_manager.close()
    print("Processo concluído. Dados salvos no banco de dados.")

if __name__ == "__main__":
    main()

