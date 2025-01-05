import pandas as pd
from botasaurus.browser import browser, Driver
import ScraperFC as sc
from bs4 import BeautifulSoup
import json
from src.dbmanager import StatisticsDatabaseManager  # Certifique-se de ajustar o caminho corretamente

feito = [
    {
        "nome_liga": "Série A do Campeonato Brasileiro",
        "temporada": "2024",
        "id_liga": "325",
        "id_temporada": "58766"
    },
    {
        "nome_liga": "Série B do Campeonato Brasileiro",
        "temporada": "2024",
        "id_liga": "390",
        "id_temporada": "59015"
    },
    {
        "nome_liga": "Primeira Divisão da Argentina",
        "temporada": "2024",
        "id_liga": "155",
        "id_temporada": "57478"
    },
    {
        "nome_liga": "Primeira Divisão do Uruguai",
        "temporada": "2024",
        "id_liga": "278",
        "id_temporada": "58264"
    }
]

ligas_futebol = [

    {
        "nome_liga": "Primeira Divisão da Colômbia",
        "temporada": "2024",
        "id_liga": "11536",
        "id_temporada": "63819"
    },
    {
        "nome_liga": "Primeira Divisão do Equador",
        "temporada": "2024",
        "id_liga": "240",
        "id_temporada": "58043"
    },
    {
        "nome_liga": "Primeira Divisão do Peru",
        "temporada": "2024",
        "id_liga": "406",
        "id_temporada": "57741"
    },
    {
        "nome_liga": "Primeira Divisão do Paraguai",
        "temporada": "2024",
        "id_liga": "11541",
        "id_temporada": "63769"
    },
    {
        "nome_liga": "Primeira Divisão da Venezuela",
        "temporada": "2024",
        "id_liga": "231",
        "id_temporada": "57694"
    },
    {
        "nome_liga": "Primeira Divisão do México",
        "temporada": "2024",
        "id_liga": "11620",
        "id_temporada": "57315"
    },
    {
        "nome_liga": "Primeira Divisão da Bolívia",
        "temporada": "2024",
        "id_liga": "16736",
        "id_temporada": "58156"
    },
    {
        "nome_liga": "Primeira Divisão do Chile",
        "temporada": "2024",
        "id_liga": "11653",
        "id_temporada": "57883"
    }
]

for liga in ligas_futebol:


    nome_liga = liga['nome_liga']
    id_liga = liga['id_liga']
    temporada = liga['id_temporada']

    print(f"Extraindo dados da liga: {nome_liga}, id: {id_liga}, temporada_id: {temporada}")

    @browser
    def get_players_stats(driver: Driver, data: dict) -> pd.DataFrame:
        league_id = id_liga
        season_id = temporada
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

    @browser
    def fetch_player_details(driver, player_id):
        """
        Fetches detailed player information using their IDs and consolidates the data into a pandas DataFrame.

        Args:
            driver (Driver): The browser driver instance used for making requests.
            player_ids (list or int): A list of player IDs or a single player ID to fetch details for.

        Returns:
            pd.DataFrame: A DataFrame containing consolidated player details.
        """
        import json
        import pandas as pd
        from bs4 import BeautifulSoup



        base_url = 'https://api.sofascore.com/api/v1/player/'  # Base URL da API

        request_url = f'{base_url}{player_id}'
        print(f"Fetching player details for ID: {player_id}")

        # Envia a requisição
        response = driver.get(request_url)
        html_content = response.get_content()

        # Usa BeautifulSoup para extrair o JSON dentro da tag <pre>
        soup = BeautifulSoup(html_content, 'html.parser')
        pre_tag = soup.find('pre')


        pre_content = pre_tag.text
        data = json.loads(pre_content)  # Converte o texto para um dicionário Python

            # Acessa os detalhes do jogador
        player_info = data.get('player', {})
        if player_info:  # Verifica se há dados para o jogador
            # Extrai os campos desejados
            extracted_data = {
            "player_id": player_info.get("id"),
            "player_name": player_info.get("name"),
            "team_name": player_info.get("team", {}).get("name"),
            "league": player_info.get("team", {}).get("tournament", {}).get("name"),
            "position": player_info.get("position"),
            "preferred_foot": player_info.get("preferredFoot"),
            "market_value": player_info.get("proposedMarketValue"),
        }
            print(extracted_data)  # Adiciona os dados à lista
       # Converte a lista de dicionários para um DataFrame

        if extracted_data:
            player_df = pd.json_normalize(extracted_data)  # Normaliza os dados JSON para o formato tabular
            #player_df = pd.DataFrame(player_df)  # Retorna um DataFrame vazio caso não haja dados
            #print(player_df.head())
        else:
            print("No player data found.")

        df = pd.json_normalize(extracted_data)
        return df.to_dict(orient='records')




    def main():
        # Caminho para o banco de dados
        db_path = "data/statistics.db"

        # Instancia o gerenciador de banco de dados
        db_manager = StatisticsDatabaseManager(db_path)

        # Executa o scraping para obter os dados
        print("Starting data scraping...")
        raw_df = get_players_stats()
        df = pd.DataFrame(raw_df)
        ## Atualizando base estatistica
        if df.empty:
            print("No data retrieved from scraping.")
        else:
            print(f"Retrieved {len(df)} records. Updating the database...")
            db_manager.insert_or_update_statistics(df)



        print(df.head())
        players_ids = df['player.id'].unique().tolist()
        print(players_ids)


        for id in players_ids:
            player_df = fetch_player_details(id)
            player_df = pd.DataFrame(player_df)
            db_manager.insert_or_update_players(player_df)


        # Fecha a conexão com o banco
        db_manager.close()
        print("Database updated successfully.")


    if __name__ == "__main__":
        main()
