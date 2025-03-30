Parece que o código contém uma linha com um comentário fora de lugar, além de problemas de indentação e um texto começando de maneira incorreta no início do código. Vou corrigir o erro e ajustar a formatação de acordo com o que foi proposto.

Aqui está o código corrigido:

```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Importar nossos módulos
from direct_scraper import get_battle_data # Updated import statement
import utils

# Importar componentes
from components.guild_overview import show_guild_overview
from components.battle_details import show_battle_details
from components.player_rankings import show_player_rankings
from components.comparison_tools import show_comparison_tools
from components.attendance_tracking import show_attendance_tracking

# Configuração básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Informações da guild
GUILD_NAME = "We Profit"
ALLIANCE_NAME = "BAHlA"

# Número mínimo de jogadores por batalha para ser considerada relevante
MIN_PLAYERS = 20

# Configurações da página
st.set_page_config(
    page_title=f"Relatório de Batalhas - {GUILD_NAME}",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Função para configurar o agendador de tarefas
def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_data, 'interval', minutes=10)
    scheduler.start()
    logging.info("Agendador iniciado - atualizações a cada 10 minutos")

# Função para atualizar os dados
def refresh_data(force_refresh=False):
    try:
        logging.info(f"Iniciando atualização {'via scraper' if force_refresh else 'automática'} dos dados")
        # Forçar atualização do scraper
        battles_df = get_battle_data(force_refresh=True)
        logging.info(f"Dados obtidos do scraper: {len(battles_df)} batalhas")
        # Salvar no estado da sessão
        st.session_state['battles_data'] = battles_df
        from datetime import timezone
        st.session_state['last_update'] = datetime.now(timezone.utc)
        logging.info(f"Dados atualizados com sucesso - {len(battles_df)} batalhas")
        return True
    except Exception as e:
        logging.error(f"Erro na atualização {'via scraper' if force_refresh else 'automática'}: {e}")
        return False

# Função para filtrar batalhas por número mínimo de jogadores
def filter_battles_by_players(battles_df, min_players=20):
    if battles_df.empty:
        return pd.DataFrame()
    return battles_df[battles_df['players'] >= min_players].reset_index(drop=True)

# Função para calcular estatísticas da guild
def calculate_guild_stats(battles_df):
    if battles_df.empty:
        return {
            'total_battles': 0,
            'total_kills': 0,
            'total_deaths': 0,
            'kd_ratio': 0,
            'win_rate': 0
        }

    total_battles = len(battles_df)
    total_kills = battles_df['kills'].sum()
    total_deaths = battles_df['deaths'].sum()
    kd_ratio = total_kills / max(1, total_deaths)

    # Consideramos vitória quando kills > deaths
    wins = sum(battles_df['kills'] > battles_df['deaths'])
    win_rate = (wins / total_battles) * 100 if total_battles > 0 else 0

    return {
        'total_battles': total_battles,
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'kd_ratio': kd_ratio,
        'win_rate': win_rate
    }

# Função para mostrar cartão de estatísticas
def show_stat_card(title, value, delta=None, delta_color="normal"):
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

# Função para obter dados de batalhas recentes
def get_recent_battles(battles_df, days=7):
    if battles_df.empty:
        return pd.DataFrame()

    # Utilizando timezone UTC para garantir compatibilidade com datetime64[ns, UTC]
    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Converter para o mesmo tipo se necessário
    if 'time' in battles_df.columns and battles_df['time'].dtype.name.startswith('datetime64'):
        # Se 'time' já é um datetime64, devemos garantir que cutoff_date também seja
        recent_battles = battles_df[battles_df['time'] >= pd.Timestamp(cutoff_date)].copy()
    else:
        # Abordagem padrão
        recent_battles = battles_df[battles_df['time'] >= cutoff_date].copy()

    # Ordenar por data (mais recentes primeiro)
    return recent_battles.sort_values('time', ascending=False)

# Função para obter estatísticas diárias
def get_daily_stats(battles_df, days=7):
    if battles_df.empty:
        return pd.DataFrame()

    # Filtrar batalhas recentes
    recent_battles = get_recent_battles(battles_df, days)
    if recent_battles.empty:
        return pd.DataFrame()

    # Copiar o dataframe para evitar avisos SettingWithCopyWarning
    recent_battles = recent_battles.copy()

    # Converter para data (sem hora) com tratamento correto para timezone
    try:
        # Usar pandas .dt para garantir compatibilidade com datetime64[ns, UTC]
        recent_battles['date'] = recent_battles['time'].dt.date
    except AttributeError:
        # Caso não seja possível usar .dt.date, tentar método alternativo
        recent_battles['date'] = recent_battles['time'].apply(lambda x: x.date())

    # Agrupar por data
    daily_stats = recent_battles.groupby('date').agg({
        'kills': 'sum',
        'deaths': 'sum'
    }).reset_index()

    # Calcular K/D ratio
    daily_stats['kd_ratio'] = daily_stats['kills'] / daily_stats['deaths'].apply(lambda x: max(x, 1))

    return daily_stats

# Função para obter top jogadores
def get_top_players(battles_df, metric='kills', limit=3):
    if battles_df.empty:
        return []

    # Extrair jogadores de todas as batalhas
    players_data = []

    for _, battle in battles_df.iterrows():
        details = battle['details']
        if GUILD_NAME in details['guilds']:
            guild_data = details['guilds'][GUILD_NAME]
            for player in guild_data['players']:
                players_data.append(player)

    if not players_data:
        return []

    # Converter para DataFrame
    players_df = pd.DataFrame(players_data)

    # Agrupar por jogador e somar métricas
    if players_df.empty:
        return []

    player_stats = players_df.groupby('name').agg({
        'kills': 'sum',
        'deaths': 'sum',
        'fame': 'sum'
    }).reset_index()

    # Calcular K/D ratio
    player_stats['kd_ratio'] = player_stats['kills'] / player_stats['deaths'].apply(lambda x: max(x, 1))

    # Ordenar e obter os top jogadores pelo métrica escolhida
    return player_stats.sort_values(metric, ascending=False).head(limit).to_dict('records')

# Função principal
def main():
    # Carregar CSS customizado
    utils.load_css()

    # Configurar o agendador de tarefas para atualizações automáticas
    setup_scheduler()

    # Inicializar o estado da sessão se não existir
    if 'battles_data' not in st.session_state:
        st.session_state['battles_data'] = get_battle_data()
        from datetime import timezone
        st.session_state['last_update'] = datetime.now(timezone.utc)
        st.session_state['selected_battle'] = None

    # Cabeçalho - Logo e título 
    from assets.logo import LOGO_SVG

    # Exibir apenas o logo
    st.markdown(LOGO_SVG, unsafe_allow_html=True)

    # Título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 36px; color: #F5B841; margin-bottom: 5px;">Relatório de Batalhas</h1>
        <h2 style="font-size: 24px; color: #F5B841; margin-bottom: 5px;">WE PROFIT</h2>
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
            <span style="background-color: #F5B841; color: #000; padding: 5px 12px; border-radius: 5px; font-weight: bold;">WE PROFIT</span>
            <span style="color: #AAAAAA;">Aliança: <span style="color: #F9F9F9; font-weight: 500;">BAHlA</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botão de atualização e informações de tempo
    col1, col2 = st.columns([2, 1])

    with col1:
        # Calcular próxima atualização automática (10 minutos após a última)
        from datetime import timezone
        last_update = st.session_state['last_update']
        next_update = last_update + timedelta(minutes=10)
        current_time = datetime.now(timezone.utc)

        # Mostrar progresso até a próxima atualização
        time_diff = (next_update - current_time).total_seconds()
        total_interval = 10 * 60  # 10 minutos em segundos
        progress = max(0, min(1.0, 1.0 - (time_diff / total_interval)))

        # Informação de tempo mais visível com um estilo personalizado
        st.markdown(f"""
        <div style="margin-bottom: 20px; padding: 15px; background-color: #242424; border-radius: 8px; border-left: 3px solid #F5B841;">
            <p style="margin: 0; font-size: 14px;">
                <span style="color: #F5B841; font-weight: 600;">⏱️ Status de Dados

:</span>
                Atualizado em <span style="font-weight: 600; color: #F9F9F9;">{last_update.strftime('%d/%m/%Y %H:%M:%S')}</span><br>
                Próxima atualização: <span style="font-weight: 600; color: #F9F9F9;">{next_update.strftime('%d/%m/%Y %H:%M:%S')}</span>
            </p>
            <p style="font-size: 13px; color: #888;">Progresso da Atualização</p>
            <div style="height: 8px; border-radius: 5px; background: linear-gradient(to right, #F5B841, #FFB83D);">
                <div style="height: 100%; width: {progress * 100}%; border-radius: 5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Mostrar botão de refresh para forçar uma nova atualização
        if st.button("🔄 Atualizar Dados"):
            if refresh_data(force_refresh=True):
                st.success("Dados atualizados com sucesso!")
            else:
                st.error("Erro ao atualizar os dados. Tente novamente.")
    
    # Exibir estatísticas da guild
    st.header("Estatísticas da Guild")
    guild_stats = calculate_guild_stats(st.session_state['battles_data'])

    # Cartões de estatísticas
    col1, col2, col3 = st.columns(3)

    with col1:
        show_stat_card("Total de Batalhas", guild_stats['total_battles'])
    with col2:
        show_stat_card("Taxa de Vitórias (%)", f"{guild_stats['win_rate']:.1f} %")
    with col3:
        show_stat_card("K/D Ratio", f"{guild_stats['kd_ratio']:.2f}")

    # Mostrar comparações de batalhas
    show_comparison_tools(st.session_state['battles_data'])

    # Mostrar detalhes das últimas batalhas
    st.header("Últimas Batalhas")
    recent_battles = get_recent_battles(st.session_state['battles_data'])

    # Caso tenha batalhas recentes
    if not recent_battles.empty:
        # Exibição das últimas batalhas
        for battle in recent_battles.head(5).iterrows():
            battle = battle[1]
            show_battle_details(battle)
    else:
        st.write("Nenhuma batalha encontrada nos últimos dias.")

    # Mostrar rankings dos jogadores
    st.header("Top Jogadores")
    top_players = get_top_players(st.session_state['battles_data'])

    # Exibir se houver dados de jogadores
    if top_players:
        show_player_rankings(top_players)
    else:
        st.write("Nenhum jogador encontrado.")
```
