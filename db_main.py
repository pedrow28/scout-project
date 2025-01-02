import pandas as pd
from botasaurus.browser import browser, Driver
import ScraperFC as sc
from bs4 import BeautifulSoup
import json
from src.dbmanager import StatisticsDatabaseManager  # Certifique-se de ajustar o caminho corretamente

ligas_futebol = [
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
    },
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
    def fetch_player_details(driver: Driver, player_ids):
        """
        Fetches detailed player information using their IDs.

        Args:
            driver (Driver): The browser driver instance.
            player_ids (list or int): List of player IDs or a single player ID.

        Returns:
            pd.DataFrame: DataFrame containing player details.
        """
        # Garantir que player_ids seja uma lista
        if isinstance(player_ids, int):  # Caso seja um único ID
            player_ids = [str(player_ids)]  # Converte para uma lista com um único elemento
        elif isinstance(player_ids, list):  # Caso seja uma lista
            player_ids = [str(pid) for pid in player_ids]  # Converte todos os elementos para string

        base_url = 'https://api.sofascore.com/api/v1/player/'
        player_data = []

        for player_id in player_ids:
            request_url = f'{base_url}{player_id}'
            print(f"Fetching player details for ID: {player_id}")
            response = driver.get(request_url)
            html_content = response.get_content()
            soup = BeautifulSoup(html_content, 'html.parser')
            pre_content = soup.find('pre').text
            data = json.loads(pre_content)

            player_data.append({
                'player_id': data.get('id'),
                'player_name': data.get('name'),
                'team_name': data.get('team', {}).get('name'),
                'league': nome_liga,
                'position': data.get('position'),
                'preferred_foot': data.get('preferredFoot'),
                'market_value': data.get('marketValue', 0)
            })

        data_player = pd.json_normalize(player_data)
        return data_player.to_dict(orient='records')



    def main():
        # Caminho para o banco de dados
        db_path = "data/statistics.db"

        # Instancia o gerenciador de banco de dados
        db_manager = StatisticsDatabaseManager(db_path)

        # Executa o scraping para obter os dados
        print("Starting data scraping...")
        raw_df = get_players_stats()
        df = pd.DataFrame(raw_df)
        players_ids = df['player.id'].unique().tolist()
        raw_players = fetch_player_details(players_ids)
        players_df = pd.DataFrame(raw_players)
        # Adicionar posição
        df = df.merge(
            players_df[['player_id', 'position']],
            left_on='player.id',
            right_on='player_id',
            how='left'
        )
        
        print(players_ids)

                # Verifica se o DataFrame contém dados
        if df.empty:
            print("No data retrieved from scraping.")
        else:
            print(f"Retrieved {len(df)} records. Updating the database...")
            db_manager.insert_or_update_statistics(df)
            db_manager.insert_or_update_players(players_df)

        

       





        # Fetch detailed player information
        print("Fetching player details...")


        

        db_manager.insert_or_update_players(players_df)




            

        # Fecha a conexão com o banco
        db_manager.close()
        print("Database updated successfully.")


    if __name__ == "__main__":
        main()
