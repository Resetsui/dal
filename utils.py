import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import random

# Importar o logotipo
from assets.logo import LOGO_SVG, ICON_SVG

# Função para carregar CSS personalizado
def load_css():
    """Load custom CSS for the dashboard"""
    st.markdown("""
    <style>
    /* Cores da WE PROFIT:
       - Dourado principal: #F5B841
       - Dourado mais escuro: #D4A12C
       - Dourado claro: #FFDB8C
       - Fundo escuro: #1A1A1A
       - Texto claro: #F9F9F9
    */

    /* Estilos globais */
    .main {
        background-color: #1A1A1A;
        color: #F9F9F9;
        font-family: 'Inter', sans-serif;
    }

    /* Estilo do header */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        justify-content: center;
    }

    .guild-logo {
        max-width: 120px;
        filter: drop-shadow(0px 0px 10px rgba(245, 184, 65, 0.5));
    }

    /* Estilo das abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #222222;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 10px 25px;
        background-color: #2A2A2A;
        color: #CCCCCC;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid #333333;
    }

    .stTabs [aria-selected="true"] {
        background-color: #F5B841;
        color: #000000 !important;
        font-weight: 600;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(245, 184, 65, 0.3);
        border: none;
    }

    /* Cartões de estatísticas */
    .stat-card {
        padding: 25px;
        border-radius: 12px;
        background-color: #242424;
        margin-bottom: 25px;
        border-left: 4px solid #F5B841;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        border-left: 6px solid #F5B841;
    }

    /* Cartões de batalha */
    .battle-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #242424;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #333333;
        position: relative;
        overflow: hidden;
    }

    .battle-card:hover {
        border-left: 5px solid #F5B841;
        transform: translateX(5px);
        background-color: #2A2A2A;
    }

    .battle-card:after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 25%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #F5B841);
    }

    /* Customização de botões */
    button[kind="primary"] {
        background-color: #F5B841 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(245, 184, 65, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(245, 184, 65, 0.4) !important;
    }

    /* Customização dos headers */
    h1, h2, h3 {
        color: #F5B841;
        font-weight: 600;
        margin-bottom: 15px;
        position: relative;
    }

    h1:after, h2:after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #F5B841, transparent);
    }

    /* Barras de progresso e spinners */
    .stProgress .st-eh {
        background-color: #F5B841 !important;
    }

    /* Alertas e notificações */
    .stAlert {
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    /* Customização dos inputs */
    input, select, textarea {
        border-radius: 8px !important;
        border: 1px solid #333333 !important;
        background-color: #2A2A2A !important;
        color: #F9F9F9 !important;
    }

    /* Customização dos sliders */
    .stSlider [data-baseweb="slider"] {
        height: 6px !important;
    }

    .stSlider [data-baseweb="thumb"] {
        height: 20px !important;
        width: 20px !important;
        background-color: #F5B841 !important;
        box-shadow: 0 2px 10px rgba(245, 184, 65, 0.3) !important;
    }

    /* Estilos para divisores */
    hr {
        border-color: #333333 !important;
        margin: 25px 0 !important;
    }

    /* Estilos para gráficos */
    .plotly-graph {
        border-radius: 12px !important;
        background-color: #242424 !important;
        padding: 15px !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para exibir o logotipo da guild
def display_logo():
    """Display the guild logo centered at the top of the page"""
    st.markdown(f"""
    <div class="header-container">
        {LOGO_SVG}
        <div style="color: #F5B841; text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5); font-size: 2.5rem; margin-left: 10px; font-weight: bold;">WE PROFIT</div>
    </div>
    """, unsafe_allow_html=True)

# Função para formatar números com separadores de milhar
def format_number(num):
    """Format numbers with commas for thousands"""
    return "{:,}".format(num)

# Função para criar um gráfico de informação simples para K/D ratio
def create_kd_gauge(kills, deaths):
    """Create a gauge chart for K/D ratio"""
    kd_ratio = kills / max(1, deaths)

    # Definir cores
    colors = {
        'low': '#ff5555',    # Vermelho para KD < 1
        'mid': '#f1fa8c',    # Amarelo para 1 <= KD < 2
        'high': '#50fa7b',   # Verde para KD >= 2
        'needle': '#bd93f9'  # Roxo para o ponteiro
    }

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=kd_ratio,
        number={'font': {'size': 40, 'color': 'white'}},
        title={
            'text': "K/D Ratio",
            'font': {'size': 24, 'color': 'white'}
        },
        delta={'reference': 1, 'increasing': {'color': colors['high']}, 'decreasing': {'color': colors['low']}},
        gauge={
            'axis': {
                'range': [None, max(2, kd_ratio)],
                'tickwidth': 1,
                'tickcolor': 'white',
                'tickfont': {'size': 14, 'color': 'white'}
            },
            'steps': [
                {'range': [0, 1], 'color': colors['low']},
                {'range': [1, 2], 'color': colors['mid']},
                {'range': [2, max(2, kd_ratio)], 'color': colors['high']}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 2},
                'thickness': 0.75,
                'value': 1
            },
            'bar': {'color': colors['needle'], 'thickness': 0.5}
        }
    ))

    fig.update_layout(
        height=400,
        font={'color': 'white', 'family': 'Arial'},
        paper_bgcolor='#282a36',
        margin={'l': 50, 'r': 50, 't': 60, 'b': 30}
    )

    return fig

# Função para criar uma visualização simples para a taxa de vitórias
def create_win_rate_gauge(win_rate, battles_won=None, total_battles=None):
    """Create a simple win rate visualization with just numbers and text"""

    # Obter a cor com base na taxa de vitória
    win_color = get_win_rate_color(win_rate)

    # Criar figura vazia
    fig = go.Figure()

    # Adicionar texto grande centralizado com valor da taxa de vitória
    fig.add_annotation(
        x=0.5, y=0.65,
        text=f"<b style='font-size:42px; color:{win_color};'>{win_rate:.1f}%</b>",
        showarrow=False,
        xref="paper",
        yref="paper"
    )

    # Adicionar título
    fig.add_annotation(
        x=0.5, y=0.9,
        text="<b style='font-size:20px; color:#F5B841;'>Taxa de Vitórias</b>",
        showarrow=False,
        xref="paper",
        yref="paper"
    )

    # Se não foram fornecidos valores específicos, calcule baseado na taxa de vitória
    if battles_won is None or total_battles is None:
        # Se não temos o total de batalhas, assuma um valor mínimo
        total_battles = total_battles or 1
        battles_won = int(round(win_rate * 0.01 * total_battles))

    fig.add_annotation(
        x=0.5, y=0.35,
        text=f"<span style='font-size:16px;'>{battles_won} Vitórias de {total_battles} Batalhas</span>",
        showarrow=False,
        xref="paper",
        yref="paper",
        font=dict(color="#AAAAAA")
    )

    # Avaliação da taxa de vitória
    if win_rate >= 60:
        assessment = "Excelente"
    elif win_rate >= 40:
        assessment = "Bom"
    else:
        assessment = "Precisa melhorar"

    fig.add_annotation(
        x=0.5, y=0.15,
        text=f"<span style='font-size:14px; color:{win_color};'>{assessment}</span>",
        showarrow=False,
        xref="paper",
        yref="paper"
    )

    # Layout simples sem eixos ou grade
    fig.update_layout(
        height=140,
        margin=dict(l=5, r=5, t=5, b=5),
        template='plotly_dark',
        paper_bgcolor='rgba(30,30,40,0.1)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            visible=False
        )
    )

    return fig

# Função para criar um gráfico de linha para estatísticas diárias
def create_daily_stats_chart(daily_stats):
    """Create a line chart for daily kills and deaths with enhanced visualizations"""
    if daily_stats.empty:
        return None

    # Converter para datetime para melhor formatação
    daily_stats['date'] = pd.to_datetime(daily_stats['date'])

    # Criar um layout mais simples e limpo com abas para diferentes visualizações
    fig = go.Figure()

    # Calcular K/D ratio para cada dia
    kd_ratios = []
    for k, d in zip(daily_stats['kills'], daily_stats['deaths']):
        kd_ratios.append(k / max(1, d))

    # Adicionar áreas para kills e mortes
    # Área de kills com preenchimento gradiente
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['kills'],
        name='Kills',
        fill='tozeroy',
        fillcolor='rgba(245, 184, 65, 0.15)',
        line=dict(color='#F5B841', width=3),
        mode='lines+markers',
        marker=dict(
            size=8, 
            symbol='circle', 
            color='#F5B841',
            line=dict(width=2, color='#1A1A1A')
        ),
        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Kills: %{y}<extra></extra>'
    ))

    # Área de mortes com preenchimento gradiente
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['deaths'],
        name='Mortes',
        fill='tozeroy',
        fillcolor='rgba(158, 158, 158, 0.1)',
        line=dict(color='#9E9E9E', width=3),
        mode='lines+markers',
        marker=dict(
            size=8, 
            symbol='circle', 
            color='#9E9E9E',
            line=dict(width=2, color='#1A1A1A')
        ),
        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Mortes: %{y}<extra></extra>'
    ))

    # Adicionar linha de K/D ratio com escala de cores
    # Criar uma escala de cores personalizada baseada nos valores
    colors = []
    for kd in kd_ratios:
        if kd < 1:
            colors.append('#FF5252')  # Vermelho
        elif kd < 2:
            colors.append('#FFC107')  # Amarelo
        else:
            colors.append('#4CAF50')  # Verde

    # Adicionar K/D ratio como bolhas coloridas e linha
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=kd_ratios,
        name='K/D Ratio',
        mode='lines+markers',
        line=dict(color='rgba(80, 250, 123, 0.5)', width=2, dash='dot'),
        marker=dict(
            size=10,
            color=colors,
            symbol='diamond',
            line=dict(width=2, color='#1A1A1A')
        ),
        yaxis='y2',
        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>K/D: %{y:.2f}<extra></extra>'
    ))

    # Melhorar layout geral
    fig.update_layout(
        title={
            'text': "Performance da Guild",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#F5B841'}
        },
        xaxis=dict(
            title=None,
            gridcolor='rgba(255, 255, 255, 0.05)',
            showgrid=False,
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickformat='%d/%m',
            tickangle=-30,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=dict(
                text="Quantidade",
                font=dict(color="#F5B841")
            ),
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False,
            showline=False,
            tickfont=dict(size=12)
        ),
        yaxis2=dict(
            title=dict(
                text="K/D Ratio",
                font=dict(color="#50fa7b")
            ),
            tickfont=dict(color="#50fa7b"),
            anchor="x",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            range=[0, max(max(kd_ratios) * 1.2, 3)]
        ),
        template='plotly_dark',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.05,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
            bgcolor='rgba(30, 30, 40, 0.7)',
            bordercolor='rgba(245, 184, 65, 0.2)',
            borderwidth=1
        ),
        hovermode="x unified"
    )

    # Adicionar uma linha de referência para K/D = 1.0
    fig.add_shape(
        type="line",
        x0=daily_stats['date'].min(),
        x1=daily_stats['date'].max(),
        y0=1.0,
        y1=1.0,
        yref="y2",
        line=dict(
            color="#50fa7b",
            width=1,
            dash="dash",
        ),
    )

    # Adicionar anotação explicativa
    fig.add_annotation(
        x=daily_stats['date'].iloc[0],
        y=1.0,
        xshift=-5,
        yshift=5,
        yref="y2",
        text="K/D = 1.0",
        showarrow=False,
        font=dict(size=10, color="#50fa7b"),
        bgcolor="rgba(0,0,0,0.5)",
        borderpad=2,
        xanchor="right"
    )

    # Adicionar anotação para o valor máximo de kills
    if len(daily_stats) > 0:
        max_kills_idx = daily_stats['kills'].argmax()
        max_kills = daily_stats['kills'].iloc[max_kills_idx]
        max_date = daily_stats['date'].iloc[max_kills_idx]

        fig.add_annotation(
            x=max_date,
            y=max_kills,
            text=f"{max_kills}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#F5B841",
            font=dict(size=10, color="#F5B841", family="Arial Black"),
            bordercolor="#F5B841",
            borderwidth=1,
            borderpad=3,
            bgcolor="rgba(26, 26, 26, 0.8)",
            opacity=0.9
        )

    return fig

# Função para criar um gráfico de barras para métricas de jogadores
def create_player_chart(players_data, metric="kills"):
    """Create a horizontal bar chart for player metrics"""
    if not players_data:
        return None

    # Converter para DataFrame
    df = pd.DataFrame(players_data)

    # Ordenar por métrica
    df = df.sort_values(metric, ascending=True)

    # Limitar a 10 jogadores
    df = df.tail(10)

    # Criar gráfico
    if metric == 'kd_ratio':
        fig = px.bar(
            df,
            x=metric,
            y='name',
            orientation='h',
            title=f"Top Jogadores por {metric.upper()}",
            labels={'name': 'Jogador', metric: metric.upper()},
            text=df[metric].apply(lambda x: f"{x:.2f}"),
            color=metric,
            color_continuous_scale=['#2A2A2A', '#F5B841'],
            hover_data={'kills': True, 'deaths': True}
        )
    else:
        fig = px.bar(
            df,
            x=metric,
            y='name',
            orientation='h',
            title=f"Top Jogadores por {metric.capitalize()}",
            labels={'name': 'Jogador', metric: metric.capitalize()},
            text=metric,
            color=metric,
            color_continuous_scale=['#2A2A2A', '#F5B841'],
            hover_data={'kills': True, 'deaths': True, 'kd_ratio': ':.2f'}
        )

    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    return fig

# Função para criar um gráfico de comparação entre guildas
def create_guild_comparison_chart(guild_stats, enemy_stats, metric="kd_ratio"):
    """Create a comparison chart between guild and enemy guilds"""
    if not enemy_stats:
        return None

    # Preparar dados
    guilds = [guild_stats['name']]
    values = [guild_stats[metric]]

    # Adicionar dados de guildas inimigas (agora enemy_stats é um dicionário)
    for guild_name, stats in enemy_stats.items():
        guilds.append(stats['name'])
        values.append(stats[metric])

    # Definir cores (destacar a guild principal com a cor dourada)
    colors = ['#F5B841'] + ['#2E2E2E'] * len(enemy_stats)

    # Formatar valores para exibição no gráfico
    if metric == 'kd_ratio':
        formatted_values = [f"{v:.2f}" for v in values]
    elif metric in ['kills', 'deaths', 'fame']:
        formatted_values = [f"{int(v):,}" for v in values]
    else:
        formatted_values = [str(v) for v in values]

    # Criar gráfico
    fig = go.Figure(go.Bar(
        x=guilds,
        y=values,
        marker_color=colors,
        text=formatted_values,
        textposition='auto'
    ))

    # Customizar layout
    title_map = {
        'kd_ratio': 'K/D Ratio',
        'kills': 'Total de Kills',
        'deaths': 'Total de Mortes',
        'fame': 'Fame Total'
    }

    fig.update_layout(
        title=f"Comparação de {title_map.get(metric, metric)}",
        xaxis_title='Guilds',
        yaxis_title=title_map.get(metric, metric),
        template='plotly_dark',
        height=400,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    return fig

# Função para obter cor com base no K/D ratio
def get_kd_color(kd_ratio):
    """Get color based on KD ratio"""
    if kd_ratio < 1:
        return '#FF5252'  # Vermelho
    elif kd_ratio < 3:
        return '#FFC107'  # Amarelo
    else:
        return '#4CAF50'  # Verde

# Função para obter cor com base na taxa de vitórias
def get_win_rate_color(win_rate):
    """Get color based on win rate"""
    if win_rate < 40:
        return '#FF5252'  # Vermelho
    elif win_rate < 60:
        return '#FFC107'  # Amarelo
    else:
        return '#4CAF50'  # Verde

# Função para exibir um card de batalha
def display_battle_card(battle, guild_name):
    """Display a single battle card with basic info"""
    # Calcular valores relevantes
    kd = battle['kills'] / max(1, battle['deaths'])
    result = "Vitória" if battle['kills'] > battle['deaths'] else "Derrota"
    result_color = "#4CAF50" if result == "Vitória" else "#FF5252"
    battle_time = battle['time'].strftime("%d/%m/%Y %H:%M")

    # Lista de jogadores para mostrar (limitado a 3)
    top_players = []
    player_count = 0

    # Usar o campo 'enemy' que foi adicionado pelo nosso scraper atualizado
    enemy_guild = battle.get('enemy', "Desconhecido")

    try:
        if 'details' in battle and 'guilds' in battle['details']:
            # Variáveis para identificar a guild principal e as inimigas
            main_guild = None

            # Identificar a guild principal e coletar os dados
            for guild, guild_stats in battle['details']['guilds'].items():
                if guild_name.lower() in guild.lower():
                    main_guild = guild
                    players = sorted(guild_stats['players'], key=lambda p: p['kills'], reverse=True)
                    for p in players[:3]:
                        top_players.append({
                            'name': p['name'],
                            'kills': p['kills'],
                            'deaths': p['deaths']
                        })
                    player_count = len(guild_stats['players'])
                    break
    except Exception as e:
        # Em caso de erro, continuamos com a lista vazia
        print(f"Erro ao processar guild inimiga: {e}")
        pass

    # Partes do HTML para montar o card
    top_players_html = ""
    if top_players:
        players_items = []
        for p in top_players:
            player_color = "#4CAF50" if p["kills"] > p["deaths"] else "#FF5252"
            kd_ratio = p["kills"] / max(1, p["deaths"])
            player_html = f'<div style="background-color: rgba(245, 184, 65, 0.1); border-radius: 6px; padding: 5px 10px; font-size: 12px; position: relative; border-left: 3px solid {player_color};"><span style="color: #F5B841; font-weight: bold;">{p["name"]}</span><div style="display: flex; gap: 10px; margin-top: 2px;"><span style="color: #4CAF50;">{p["kills"]} K</span><span style="color: #FF5252;">{p["deaths"]} D</span><span style="color: #F5B841;">{kd_ratio:.1f} K/D</span></div></div>'
            players_items.append(player_html)

        players_list = "".join(players_items)
        top_players_html = f'<div style="margin-top: 15px; background-color: rgba(0,0,0,0.15); padding: 12px; border-radius: 8px;"><div style="font-size: 14px; color: #F5B841; margin-bottom: 10px; font-weight: bold;"><svg width="16" height="16" style="vertical-align: middle; margin-right: 5px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#F5B841"/></svg>Top Players</div><div style="display: flex; flex-wrap: wrap; gap: 10px;">{players_list}</div></div>'

    # HTML do card principal
    html = f'''
    <div style="background-color: rgba(30, 30, 40, 0.4); padding: 18px; border-radius: 10px; margin: 15px 0; border: 1px solid rgba(245, 184, 65, 0.15); position: relative; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);">
        <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: {result_color};"></div>
        <div style="position: absolute; top: 0; right: 0; width: 100px; height: 100px; background: radial-gradient(circle at top right, rgba(245, 184, 65, 0.15), transparent 70%); border-radius: 50%;"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <span style="color: #AAAAAA; font-size: 12px;">{battle_time}</span>
                <div style="font-weight: bold; margin-top: 5px; color: #F5B841; font-size: 16px;">{player_count} jogadores</div>
                <div style="margin-top: 8px; padding: 5px 8px; background-color: rgba(255,82,82,0.1); border-radius: 4px; border-left: 3px solid #FF5252;">
                    <span style="font-size: 13px; color: #AAAAAA;">VS</span> 
                    <span style="font-size: 15px; color: #FF5252; font-weight: 600; margin-left: 5px;">{enemy_guild}</span>
                </div>
            </div>
            <div>
                <span style="background-color: {result_color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{result}</span></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 15px 0; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
            <div style="text-align: center; padding: 0 15px;">
                <div style="font-size: 22px; font-weight: bold; color: #4CAF50;">{battle['kills']}</div>
                <div style="font-size: 12px; color: #AAAAAA;">Kills</div>
            </div>
            <div style="text-align: center; padding: 0 15px; border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 22px; font-weight: bold; color: #FF5252;">{battle['deaths']}</div>
                <div style="font-size: 12px; color: #AAAAAA;">Mortes</div>
            </div>
            <div style="text-align: center; padding: 0 15px;">
                <div style="font-size: 22px; font-weight: bold; color: #F5B841;">{kd:.2f}</div>
                <div style="font-size: 12px; color: #AAAAAA;">K/D</div>
            </div>
        </div>
        {top_players_html}
    </div>
    '''

    # Renderizar o HTML
    st.markdown(html, unsafe_allow_html=True)