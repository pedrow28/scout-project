
# 🚀 Scout Project – Análise Inteligente de Jogadores de Futebol

## 📌 Visão Geral

O **Scout Project** é uma ferramenta de **scouting e análise de desempenho de jogadores de futebol**, utilizando **web scraping, banco de dados e inteligência artificial**. O projeto coleta estatísticas detalhadas de diversas ligas, armazena os dados em um banco SQLite, processa informações com IA (CrewAI) e gera **relatórios estruturados em Markdown e PDF**.

O objetivo é **auxiliar clubes e analistas** na identificação de talentos e tomada de decisão, combinando **desempenho estatístico e custo-benefício**.

---

## 📊 Funcionalidades

✅ **Web Scraping Automatizado** → Coleta estatísticas de jogadores usando a API do **SofaScore**.  
✅ **Banco de Dados Estruturado** → Armazena e organiza os dados no SQLite para análise posterior.  
✅ **Análise de Desempenho** → Aplica métricas personalizadas para ranquear jogadores por posição.  
✅ **Geração de Relatórios** → Cria relatórios detalhados em **Markdown e PDF** para auxiliar na tomada de decisão.  
✅ **Pipeline Automatizado** → Integra **CrewAI** para análise inteligente e escrita dos relatórios.  

---

## 📂 Estrutura do Projeto

```
📦 pedrow28-scout-project
├── db_main.py                   # Script principal para scraping e armazenamento no banco de dados
├── requirements.txt              # Dependências do projeto
├── report.md                     # Relatório gerado com análise dos jogadores
├── output/                        # Diretório onde os relatórios e estatísticas processadas são armazenados
│   ├── fetch_player_details.json  # Dados coletados de jogadores
│   ├── fetch_player_stats.json    # Estatísticas de jogadores
│   ├── report_cleaned.md          # Relatório final formatado
│   └── run_scraper_and_update_db.json # Status da atualização do banco
├── error_logs/                    # Diretório contendo logs de erros durante scraping
├── scout_crew/                     # Diretório contendo a lógica de IA baseada no CrewAI
│   ├── README.md                  # Explicação sobre os agentes da IA
│   ├── main.py                    # Script principal do CrewAI
│   ├── src/                        # Código-fonte do CrewAI
│   │   ├── crew.py                # Definição dos agentes de IA
│   │   ├── config/
│   │   │   ├── agents.yaml         # Configuração dos agentes da IA
│   │   │   ├── tasks.yaml          # Configuração das tarefas de análise
│   │   └── tools/
│   │       ├── sql_tools.py        # Ferramentas para manipulação do banco SQL
├── src/                            # Código principal do projeto
│   ├── dbmanager.py                # Gerenciamento do banco de dados SQLite
│   ├── iterator.py                 # Iteração sobre jogadores coletados
│   └── scrapper.py                 # Script de scraping para obtenção dos dados
└── README.md                       # Este arquivo
```

---

## 🔥 Pipeline do Projeto

O projeto segue um fluxo estruturado dividido em cinco fases principais:

1️⃣ **Coleta de Dados (Web Scraping)** → Extração de estatísticas da API do SofaScore via `db_main.py`.  
2️⃣ **Armazenamento e Processamento** → Inserção e atualização no **banco de dados SQLite** (`statistics.db`).  
3️⃣ **Análise e Ranking dos Jogadores** → Cálculo de **índices compostos** para selecionar os melhores atletas.  
4️⃣ **Geração de Relatórios** → Criação automática de **relatórios detalhados em Markdown e PDF**.  
5️⃣ **Exportação e Uso** → Disponibilização dos relatórios para clubes, analistas e scouts.  

---

## 🛠️ Instalação e Configuração

### **1. Pré-requisitos**
- **Python** `>= 3.10`
- **pip** instalado
- **SQLite** para armazenamento dos dados

### **2. Clonar o Repositório**
```bash
git clone https://github.com/seu-usuario/pedrow28-scout-project.git
cd pedrow28-scout-project
```

### **3. Instalar as Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configurar as Chaves de API**
- O projeto faz scraping da **API da OpenAI**. Configure a chave de API no arquivo `.env`:
```ini
OPENAI_API_KEY=your_api_key_here
```

### **5. Executar o Pipeline**
Para rodar a análise completa:
```bash
python db_main.py
```

Se quiser apenas gerar um relatório baseado nos dados já coletados:
```bash
python scout_crew/main.py
```

---

## 📜 Exemplos de Uso

### **1. Exemplo de Saída JSON (Dados do Jogador)**
```json
{
  "player_id": 293341,
  "player_name": "Rodrigo Contreras",
  "age": 29,
  "team_name": "Antofagasta",
  "league": "Primera División",
  "position": "ST",
  "preferred_foot": "Left",
  "market_value": 1600000
}
```

### **2. Exemplo de Trecho do Relatório**
```markdown
# Relatório de Análise de Jogadores

## 🏆 1. Resumo Executivo

- **Objetivo:** Identificar laterais-direitos sub-25 com maior potencial.
- **Jogadores Avaliados:** 30
- **Melhor Índice Composto:** Joaquín García (Vélez Sarsfield)

## 📊 2. Análise Individual

### Joaquín García (Vélez Sarsfield)
- **Valor de Mercado:** $3.400.000
- **Aparições:** 22 jogos
- **Duelos Vencidos:** 62,44%
- **Assistências:** 0
- **Precisão de Passe:** 83,16%
- **Índice Composto:** 32,53

## 🏅 3. Recomendações
1. **Joaquín García** – Melhor custo-benefício e maior precisão de passes.
2. **Bautista Barros Schelotto** – Alto potencial de valorização no mercado.
```

---

## 📌 Contribuição

Se você deseja contribuir para este projeto:

1. **Crie um fork** do repositório.
2. **Crie uma branch** para sua funcionalidade (`git checkout -b minha-feature`).
3. **Faça commits** das suas alterações (`git commit -m "Minha contribuição"`).
4. **Envie um pull request** para análise.

---

## 📃 Licença

Este projeto está sob a licença **MIT**. Sinta-se à vontade para usá-lo e modificá-lo conforme necessário.

---

## 🤝 Contato

Caso tenha dúvidas ou sugestões, entre em contato:

- **Autor:** Pedro William Ribeiro Diniz
- [**E-mail**](mailto:pedrowilliamrd@gmail.com)
- [**LinkedIn:**](https://www.linkedin.com/in/pedrowilliamrd/)
- [**GitHub:**](https://github.com/pedrow28)

---

🔥 **Scout Project** – Transformando estatísticas em insights para o futebol! ⚽📊
```

