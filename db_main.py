"""

Constrói a base de dados de jogadores a partir de scouts da liga selecionada e
exporta para a base geral.


"""

from src.iterator import LeagueScraper
from src.scrapper import PlayerScoutScraper
import time

def main():
    # 1. Criar o scraper para a liga (gera o dicionário de URLs dos times)
    league_url = "https://fbref.com/pt/comps/24/Serie-A-Estatisticas"
    league_scraper = LeagueScraper(league_url)
    teams_data = league_scraper.run()  # Retorna o dicionário de times e suas URLs
    print(f"URLs dos times extraídas: {teams_data}")

    time.sleep(60)

    # 2. Criar o scraper para os scouts dos jogadores
    player_scraper = PlayerScoutScraper(teams_data)
    scout_data = player_scraper.run()  # Retorna o DataFrame consolidado
    print(scout_data.head())  # Exibe as primeiras linhas para verificação

    # 3. Exportar os resultados para um arquivo CSV
    output_file = "data/tabela_jogadores.csv"
    scout_data.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';')
    print(f"Dados exportados para {output_file}")

if __name__ == "__main__":
    main()

