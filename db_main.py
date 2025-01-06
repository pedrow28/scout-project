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
    }]


ligas_futebol = [
    {
        "nome_liga": "Primeira Divisão do Chile",
        "temporada": "2024",
        "id_liga": "11653",
        "id_temporada": "57883"
    },
    {
        "nome_liga": "Primeira Divisão de Senegal",
        "temporada": "2024",
        "id_liga": "1226",
        "id_temporada": "56126"
    },
    {
        "nome_liga": "Primeira Divisão de Angola",
        "temporada": "2024",
        "id_liga": "2308",
        "id_temporada": "56180"
    },
    {
        "nome_liga": "Primeira Divisão de Marrocos",
        "temporada": "2024",
        "id_liga": "937",
        "id_temporada": "65433"
    },
    {
        "nome_liga": "Primeira Divisão de Nigéria",
        "temporada": "2024",
        "id_liga": "2060",
        "id_temporada": "55468"
    },
    {
        "nome_liga": "Primeira Divisão da África do Sul",
        "temporada": "2024",
        "id_liga": "358",
        "id_temporada": "53301"
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
        from datetime import datetime



        base_url = 'https://api.sofascore.com/api/v1/player/'  # Base URL da API
        
        

        request_url = f'{base_url}{player_id}'
        position_request_url = f"https://www.sofascore.com/api/v1/player/{player_id}/characteristics"
        print(f"Fetching player details for ID: {player_id}")

        def fetch_data_from_api(driver, request_url):
            # Envia a requisição
            response = driver.get(request_url)
            html_content = response.get_content()

            # Usa BeautifulSoup para extrair o JSON dentro da tag <pre>
            soup = BeautifulSoup(html_content, 'html.parser')
            pre_tag = soup.find('pre')

            pre_content = pre_tag.text
            data = json.loads(pre_content)  # Converte o texto para um dicionário Python
            return data

        # Acessa os detalhes do jogador
        data_player = fetch_data_from_api(driver, request_url)
        player_info = data_player.get('player', {})
        data_position = fetch_data_from_api(driver, position_request_url)
        positions_str = " - ".join(data_position["positions"])
        if player_info and positions_str:  # Verifica se há dados para o jogador
            

            # Timestamp fornecido
            dateOfBirthTimestamp = player_info.get("dateOfBirthTimestamp")

            if dateOfBirthTimestamp is not None:

                # Converter o timestamp em uma data
                date_of_birth = datetime.fromtimestamp(dateOfBirthTimestamp)
                
                # Obter a data atual
                today = datetime.now()

                # Calcular a idade
                age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

                print(f"A idade é: {age} anos")
            else:
                age = None


            extracted_data = {
            "player_id": player_info.get("id"),
            "player_name": player_info.get("name"),
            "age": age,
            "team_name": player_info.get("team", {}).get("name"),
            "league": player_info.get("team", {}).get("tournament", {}).get("name"),
            "position": positions_str,
            "preferred_foot": player_info.get("preferredFoot"),
            "market_value": player_info.get("proposedMarketValue"),
        }
            print(extracted_data)  # Adiciona os dados à lista
            df = pd.json_normalize(extracted_data)
            return df.to_dict(orient='records')
        else:
            print("Dados não encontrados para o jogador.")
       






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
