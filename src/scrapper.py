import requests
from bs4 import BeautifulSoup
import cloudscraper
import pandas as pd

# Seções da tabela, em ordem
sections = [
    "Estatísticas Padrão",
    "Chutes",
    "Passes",
    "Gols e Criação de Chutes",
    "Defesa",
    "Posse",
    "Estatísticas Variadas"
]

scraper = cloudscraper.create_scraper()

# URL da página
url = "https://fbref.com/pt/jogadores/d637fc22/scout/365_m2/Relatorio-de-Observacao-de-Rodrigo-Battaglia"

response = scraper.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Localizar a tabela principal que contém todas as informações
    table = soup.find('table', {'id': 'scout_full_CB'})  # Ajuste o ID conforme necessário

    if table:
        rows = table.find_all('tr')  # Todas as linhas da tabela
        data = []
        current_section = None

        for row in rows:
            # Extrair células da linha
            cells = [cell.text.strip() for cell in row.find_all(['th', 'td'])]

            # Verificar se a linha é uma nova seção
            if len(cells) == 1 and cells[0] in sections:
                current_section = cells[0]  # Atualizar a seção atual
            elif len(cells) == 3 and current_section:  # Linha válida com 3 colunas
                data.append([current_section] + cells)

        # Criar o DataFrame
        df = pd.DataFrame(data, columns=['Seção', 'Estatística', 'Por 90', 'Percentil'])

        # Filtrar linhas vazias ou repetitivas
        df = df[df['Estatística'].str.lower() != 'estatística']  # Remove linhas com "Estatística"
        df = df.dropna()  # Remove linhas com valores nulos
        df = df[~((df['Por 90'].isna()) & (df['Percentil'].isna()))]  # Remove linhas vazias nas colunas numéricas

        # Ajustar colunas numéricas
        df['Por 90'] = pd.to_numeric(df['Por 90'], errors='coerce')
        df['Percentil'] = pd.to_numeric(df['Percentil'], errors='coerce')

        # Exibir e salvar os dados
        print(df.head())
        df.to_csv('data/tabela_filtrada.csv', index=False, encoding='utf-8-sig', sep=';')
    else:
        print("Tabela principal não encontrada.")
else:
    print(f"Erro ao acessar a página: {response.status_code}")
