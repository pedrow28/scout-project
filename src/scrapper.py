import requests
import re
from bs4 import BeautifulSoup
import cloudscraper
import pandas as pd
from datetime import datetime

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
url = "https://fbref.com/pt/jogadores/33a1f72e/scout/365_m2/Relatorio-de-Observacao-de-Hulk"

response = scraper.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Extrair Nome, Clube, Idade, Posição e Pé Favorito
    meta_div = soup.find('div', {'id': 'meta'})
    if meta_div:
        # Nome do jogador
        nome_jogador = meta_div.find('h1').text.strip()

        # Posição e Pé favorito
        posicao_e_pe = meta_div.find_all('p')[1].text  # Segundo <p> contém "Posição" e "Pé favorito"
        posicao = posicao_e_pe.split("Posição:")[1].split("•")[0].strip() if "Posição:" in posicao_e_pe else "Desconhecida"
        pe_favorito = posicao_e_pe.split("Pé favorito:")[1].strip() if "Pé favorito:" in posicao_e_pe else "Desconhecido"

        # Extrair data de nascimento e calcular idade
        data_nascimento_span = meta_div.find('span', {'id': 'necro-birth'})
        if data_nascimento_span and 'data-birth' in data_nascimento_span.attrs:
            data_nascimento_str = data_nascimento_span['data-birth']
            data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
            hoje = datetime.now().date()
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        else:
            idade = "Desconhecida"

        # Buscar diretamente pelo <strong> com "Clube:"
        clube_strong = meta_div.find('strong', string=lambda text: text and "Clube:" in text)
        if clube_strong:
            # Encontrar o parágrafo pai (<p>) e o link dentro dele
            clube_p = clube_strong.find_parent('p')  # Retorna o <p> que contém o <strong>
            if clube_p:
                clube_link = clube_p.find('a')  # Busca o <a> dentro do <p>
                clube = clube_link.text.strip() if clube_link else "Desconhecido (link não encontrado)"
            else:
                clube = "Desconhecido (parágrafo não encontrado)"
        else:
            clube = "Desconhecido (strong não encontrado)"

        
    else:
        nome_jogador, posicao, pe_favorito, clube, idade = (
            "Desconhecido", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecida"
        )

    # 2. Localizar a tabela principal que contém todas as informações
    table = soup.find('table', {'id': re.compile(r'^scout_full_')})  # Ajuste o ID conforme necessário

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

        # Filtrar linhas com "Estatística" vazia
        df = df[df['Estatística'].notna()]  # Remove linhas com valores NaN em "Estatística"
        df = df[df['Estatística'] != ""]   # Remove linhas com "Estatística" vazia

        # Ajustar colunas numéricas
        df['Por 90'] = pd.to_numeric(df['Por 90'], errors='coerce')
        df['Percentil'] = pd.to_numeric(df['Percentil'], errors='coerce')

        # Adicionar colunas extras
        df.insert(0, 'Nome do Jogador', nome_jogador)  # Nome do jogador
        df.insert(1, 'Clube', clube)  # Clube
        df.insert(2, 'Idade', idade)  # Idade
        df.insert(3, 'Posição', posicao)  # Posição
        df.insert(4, 'Pé Favorito', pe_favorito)  # Pé favorito
        df['Data de Extração'] = datetime.now().strftime('%Y-%m-%d')  # Data atual

        # Ajustar a coluna Posição para remover texto após "▪"
        df['Posição'] = df['Posição'].str.split('▪').str[0].str.strip()

        # Exibir e salvar os dados
        print(df.head())
        df.to_csv('data/tabela_completa.csv', index=False, encoding='utf-8-sig', sep=';')
    else:
        print("Tabela principal não encontrada.")
else:
    print(f"Erro ao acessar a página: {response.status_code}")
