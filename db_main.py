import pandas as pd
from botasaurus.browser import browser, Driver
import ScraperFC as sc
from bs4 import BeautifulSoup
import json
from src.dbmanager import StatisticsDatabaseManager  # Certifique-se de ajustar o caminho corretamente


@browser
def get_players_stats(driver: Driver, data: dict) -> pd.DataFrame:
    league_id = "325"
    season_id = "58766"
    offset = 0
    accumulation = 'total'
    self = sc.Sofascore()

    results = []
    while True:
        request_url = (
            'https://api.sofascore.com/api/v1'
            f'/unique-tournament/{league_id}/season/{season_id}/statistics'
            f'?limit=100&offset={offset}'
            f'&accumulation={accumulation}'
            f'&fields={self.concatenated_fields}'
        )

        print(f"Fetching data from: {request_url}")

        response = driver.get(request_url)
        html_content = response.get_content()

        # Parse o HTML usando BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontre o conteúdo da tag <pre>
        pre_content = soup.find('pre').text

        # Carregue o JSON a partir do texto
        data = json.loads(pre_content)

        # Acesse os resultados e acumule-os
        new_results = data.get('results', [])
        results.extend(new_results)

        # Verifique se há mais páginas para processar
        if len(new_results) < 100:
            break

        offset += 100

    # Transformar os resultados acumulados em um DataFrame
    if not results:
        print("No data retrieved.")
        return pd.DataFrame()

    # Flatten todos os campos retornados no JSON
    df = pd.json_normalize(results)
    return df.to_dict(orient='records')  # Retorna como lista de dicionários


def main():
    # Caminho para o banco de dados
    db_path = "statistics.db"

    # Instancia o gerenciador de banco de dados
    db_manager = StatisticsDatabaseManager(db_path)

    # Executa o scraping para obter os dados
    print("Starting data scraping...")
    raw_df = get_players_stats()
    df = pd.DataFrame(raw_df)

    # Verifica se o DataFrame contém dados
    if df.empty:
        print("No data retrieved from scraping.")
    else:
        print(f"Retrieved {len(df)} records. Updating the database...")
        db_manager.insert_or_update_statistics(df)

    # Fecha a conexão com o banco
    db_manager.close()
    print("Database updated successfully.")


if __name__ == "__main__":
    main()
