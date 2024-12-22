import requests
from bs4 import BeautifulSoup
import cloudscraper
import pandas as pd

scraper = cloudscraper.create_scraper()

# URL da página
url = "https://fbref.com/pt/jogadores/d637fc22/scout/365_m2/Relatorio-de-Observacao-de-Rodrigo-Battaglia"

response = scraper.get(url)



# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'scout_full_CB'})  # Ajuste para o ID correto

    if table:
        # Extrair os cabeçalhos
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]

        # Extrair as linhas
        rows = []
        for row in table.find('tbody').find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            rows.append(cells)

        # Ajustar desigualdades entre headers e rows
        for i, row in enumerate(rows):
            if len(row) < len(headers):
                rows[i] += [''] * (len(headers) - len(row))

        # Criar DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Exibir o DataFrame
        print(df)

        # Salvar o DataFrame em CSV (opcional)
        df.to_csv('tabela_extracao.csv', index=False)
    else:
        print("Tabela não encontrada. Verifique o seletor.")
else:
    print(f"Erro ao acessar a página: {response.status_code}")
