import pandas as pd
from botasaurus.browser import browser, Driver
import ScraperFC as sc
from bs4 import BeautifulSoup
import json

class SofaScoreScraper:
    def __init__(self):
        # Base URL da API SofaScore
        self.base_url = 'https://api.sofascore.com/api/v1'
        # Cabeçalhos padrão para as requisições HTTP
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
        }
        # Tipo de acumulação de dados ("total")
        self.accumulation = 'total'

    @browser
    def fetch_player_stats(self, driver: Driver, data: dict) -> pd.DataFrame:
        """
        Coleta estatísticas dos jogadores de uma liga e temporada específicas.

        Args:
            driver (Driver): Instância do driver fornecido pelo botasaurus.
            league_id (str): ID da liga a ser consultada.
            season_id (str): ID da temporada a ser consultada.

        Returns:
            pd.DataFrame: DataFrame contendo as estatísticas dos jogadores.
        """
        league_id = "325"
        season_id = "58766"

        offset = 0  # Controle de paginação
        results = []  # Lista para armazenar os resultados acumulados
        
        while True:
            # Monta a URL da requisição usando os parâmetros da API
            request_url = (
                f'{self.base_url}/unique-tournament/{league_id}/season/{season_id}/statistics'
                f'?limit=100&offset={offset}'  # Limite e offset para paginação
                f'&accumulation={self.accumulation}'  # Tipo de acumulação
                f'&fields={sc.Sofascore().concatenated_fields}'  # Campos desejados na resposta
            )

            print(f"Fetching URL: {request_url}")

            # Realiza a requisição HTTP utilizando o driver
            response = driver.get(request_url)
            html_content = response.get_content()

            # Analisa o HTML retornado para extrair o conteúdo JSON
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extrai o texto da tag <pre> contendo o JSON
            pre_content = soup.find('pre').text

            # Converte o texto JSON em um dicionário Python
            data = json.loads(pre_content)

            # Extrai os resultados da resposta e os acumula
            new_results = data.get('results', [])
            results.extend(new_results)

            # Verifica se a página atual contém menos de 100 resultados (última página)
            if len(new_results) < 100:
                break

            # Incrementa o offset para buscar a próxima página
            offset += 100

        # Verifica se há resultados e cria o DataFrame
        if not results:
            return pd.DataFrame()  # Retorna um DataFrame vazio se nenhum dado foi encontrado

        # Converte os resultados acumulados em um DataFrame
        df = pd.json_normalize(results)  # Expande campos aninhados
        return df

