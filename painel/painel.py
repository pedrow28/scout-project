import streamlit as st
import sqlite3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import io

# Configuração do banco de dados
DB_PATH = "statistics.db"

# Mapeamento de prioridades para valores numéricos
priority_weights = {"Baixo": 0.5, "Médio": 1.0, "Alto": 1.5}

# Função para o Radar Chart
def show_radar_chart(dataframe, selected_stats):
    if len(dataframe) > 0 and selected_stats:
        top_5 = dataframe.nlargest(5, "composite_index")  # Seleciona os 5 melhores
        radar_data = top_5.melt(
            id_vars=["player_name"],
            value_vars=selected_stats,
            var_name="Métricas",
            value_name="Valor"
        )
        fig = px.line_polar(
            radar_data,
            r="Valor",
            theta="Métricas",
            color="player_name",
            line_close=True,
            template="plotly_dark"
        )
        fig.update_layout(
            title="Comparação dos 5 Melhores Jogadores (Radar Chart)",
            polar=dict(
                radialaxis=dict(visible=True, range=[0, radar_data["Valor"].max() * 1.1])
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione pelo menos uma estatística válida para o gráfico de radar.")

# Função para Scatter Plot
def show_scatter_plot(dataframe, x_axis, y_axis):
    if x_axis and y_axis and x_axis in dataframe.columns and y_axis in dataframe.columns:
        fig = px.scatter(
            dataframe,
            x=x_axis,
            y=y_axis,
            color="position",
            size="market_value",
            hover_name="player_name",
            title=f"{x_axis} x {y_axis} (Gráfico de Dispersão)",
            labels={x_axis: x_axis.replace("_", " ").title(), y_axis: y_axis.replace("_", " ").title()}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione pelo menos duas estatísticas diferentes para criar o gráfico de dispersão.")

# Função para buscar ligas disponíveis
def get_available_leagues():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT league FROM players"
    leagues = pd.read_sql_query(query, conn)['league'].tolist()
    conn.close()
    return leagues

# Função para exibir a tabela interativa
def show_interactive_table(dataframe):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_pagination(enabled=True)
    gb.configure_side_bar()
    gb.configure_selection(selection_mode="single")
    gb.configure_default_column(editable=False, filter=True, sortable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        dataframe,
        gridOptions=grid_options,
        height=400,
        theme="streamlit",
        enable_enterprise_modules=True,
        update_mode="MODEL_CHANGED",
    )

    return grid_response

# Função para realizar a pesquisa
def search_players(selected_stats, priorities, leagues, positions, min_market_value, max_market_value, min_age, max_age, min_appearances, min_minutes):
    all_stats = [
        "goals", "yellow_cards", "red_cards", "ground_duels_won", "ground_duels_won_percentage",
        "aerial_duels_won", "aerial_duels_won_percentage", "successful_dribbles",
        "successful_dribbles_percentage", "tackles", "assists", "accurate_passes_percentage",
        "total_duels_won", "total_duels_won_percentage", "minutes_played", "was_fouled",
        "fouls", "dispossessed", "appearances", "saves", "interceptions", "shots_on_target", "expected_goals"
    ]
    prefixed_all_stats = [f"s.{stat}" for stat in all_stats]
    index_formula = " + ".join([f"{priority_weights[priorities[stat]]} * s.{stat}" for stat in selected_stats])
    
    league_filter = "1=1" if "Todas" in leagues else f"p.league IN ({', '.join(['?'] * len(leagues))})"
    position_filter = " OR ".join([f"p.position LIKE '%{position.split('(')[1][:-1]}%'" for position in positions])
    position_filter = f"({position_filter})" if positions else "1=1"

    query = f"""
    SELECT p.player_id, p.player_name, p.team_name, p.league, p.market_value, p.age, p.preferred_foot, p.position,
           {", ".join(prefixed_all_stats)},
           ({index_formula}) AS composite_index
    FROM players p
    JOIN statistics s ON p.player_id = s.player_id
    WHERE {league_filter}
      AND {position_filter}
      AND p.market_value BETWEEN ? AND ?
      AND p.age BETWEEN ? AND ?
      AND (s.appearances >= ? OR s.minutes_played >= ?)
    ORDER BY composite_index DESC
    LIMIT 30;
    """
    conn = sqlite3.connect(DB_PATH)
    params = leagues + [min_market_value, max_market_value, min_age, max_age, min_appearances, min_minutes] if "Todas" not in leagues else [min_market_value, max_market_value, min_age, max_age, min_appearances, min_minutes]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Função para exportar dados
def add_export_button(dataframe):
    if not dataframe.empty:
        csv = dataframe.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Resultados em CSV",
            data=csv,
            file_name="resultados_jogadores.csv",
            mime="text/csv",
        )

# Sidebar
st.sidebar.title("Parâmetros de Busca")
positions = st.sidebar.multiselect("Selecione as Posições", [
        "Atacante Central (ST)",
        "Ponta Esquerda (LW)",
        "Ponta Direita (RW)",
        "Meio-campista Ofensivo (AM)",
        "Meio-campista Esquerdo (ML)",
        "Meio-campista Central (MC)",
        "Meio-campista Direito (MR)",
        "Volante (DM)",
        "Lateral Esquerdo (DL)",
        "Zagueiro Central (DC)",
        "Lateral Direito (DR)",
        "Goleiro (GK)"
    ], default=[])
# Dicionário de tradução
stats_translation = {
    "goals": "Gols Marcados",
    "yellow_cards": "Cartões Amarelos",
    "red_cards": "Cartões Vermelhos",
    "ground_duels_won": "Duelos no Chão Vencidos",
    "ground_duels_won_percentage": "Porcentagem de Duelos no Chão Vencidos",
    "aerial_duels_won": "Duelos Aéreos Vencidos",
    "aerial_duels_won_percentage": "Porcentagem de Duelos Aéreos Vencidos",
    "successful_dribbles": "Dribles Bem Sucedidos",
    "successful_dribbles_percentage": "Porcentagem de Dribles Bem Sucedidos",
    "tackles": "Desarmes",
    "assists": "Assistências",
    "accurate_passes_percentage": "Porcentagem de Passes Precisos",
    "total_duels_won": "Total de Duelos Vencidos",
    "total_duels_won_percentage": "Porcentagem Total de Duelos Vencidos",
    "minutes_played": "Minutos Jogados",
    "was_fouled": "Faltas Sofridas",
    "fouls": "Faltas Cometidas",
    "dispossessed": "Perdas de Posse de Bola",
    "appearances": "Aparições em Jogos",
    "saves": "Defesas",
    "interceptions": "Interceptações",
    "shots_on_target": "Chutes no Gol",
    "expected_goals": "Gols Esperados (xG)"
}

# Obter lista traduzida
translated_stats = list(stats_translation.values())
available_stats = list(stats_translation.keys())

# Estatísticas para Pesquisa (barra lateral)
selected_stats_translated = st.sidebar.multiselect(
    "Estatísticas Disponíveis para Pesquisa",
    options=translated_stats,  # Exibir as estatísticas traduzidas
    default=[stats_translation["goals"], stats_translation["assists"]]
)




all_leagues = ["Todas"] + get_available_leagues()
leagues = st.sidebar.multiselect("Selecione as Ligas", options=all_leagues, default=["Todas"])
min_market_value = st.sidebar.slider("Valor de Mercado Mínimo (em milhões)", 0, 50, 0)
max_market_value = st.sidebar.slider("Valor de Mercado Máximo (em milhões)", min_market_value, 100, 50)
# Atualização na barra lateral
min_age = st.sidebar.slider("Idade Mínima", 16, 40, 18)  # Adicionei idade mínima
max_age = st.sidebar.slider("Idade Máxima", min_age, 40, 30)  # Adicionei idade máxima
min_appearances = st.sidebar.number_input("Mínimo de Aparições", value=10, step=1)
min_minutes = st.sidebar.number_input("Mínimo de Minutos Jogados", value=500, step=100)



# Converter as escolhas de volta para os nomes originais (inglês)
selected_stats = [key for key, value in stats_translation.items() if value in selected_stats_translated]


# Prioridades para as Estatísticas Selecionadas
priorities_translated = {}
for stat_translated in selected_stats_translated:
    stat_key = [key for key, value in stats_translation.items() if value == stat_translated][0]
    priorities_translated[stat_key] = st.sidebar.selectbox(
        f"Prioridade para {stat_translated}",
        ["Baixo", "Médio", "Alto"],
        index=1
    )

# Seção 2: Estatísticas para Gráficos
st.sidebar.subheader("Configurações de Gráficos")



# Estatísticas para Radar (barra lateral)
radar_stats_translated = st.sidebar.multiselect(
    "Estatísticas para Radar",
    options=translated_stats,
    default=[stats_translation["goals"], stats_translation["assists"], stats_translation["shots_on_target"]]
)
# Estatísticas para Dispersão (barra lateral)
scatter_x_translated = st.sidebar.selectbox(
    "Eixo X (Dispersão)",
    options=translated_stats,
    index=translated_stats.index(stats_translation["goals"])
)
scatter_y_translated = st.sidebar.selectbox(
    "Eixo Y (Dispersão)",
    options=translated_stats,
    index=translated_stats.index(stats_translation["assists"])
)

# Main Section
st.title("Painel de Scout de Jogadores")

# Converter de volta para chaves originais (inglês)
radar_stats = [key for key, value in stats_translation.items() if value in radar_stats_translated]
scatter_x = [key for key, value in stats_translation.items() if value == scatter_x_translated][0]
scatter_y = [key for key, value in stats_translation.items() if value == scatter_y_translated][0]

# Botão para buscar jogadores
if st.sidebar.button("Buscar"):
    with st.spinner("Carregando dados..."):
        df = search_players(
            selected_stats,  # Nomes originais
            priorities_translated,  # Prioridades em inglês
            leagues, positions,
            min_market_value * 1e6, max_market_value * 1e6,
            min_age, max_age,  # Passa as idades mínima e máxima
            min_appearances, min_minutes
        )
        
        if not df.empty:
            st.subheader("Tabela de Resultados")
            grid_response = show_interactive_table(df)
            add_export_button(df)

            st.subheader("Gráficos de Análise")
            show_radar_chart(df, radar_stats)
            show_scatter_plot(df, scatter_x, scatter_y)
        else:
            st.warning("Nenhum jogador encontrado para os parâmetros selecionados.")


