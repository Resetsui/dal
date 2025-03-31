import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import time

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

# Função para mostrar detalhes de uma batalha (mantida para compatibilidade)
def show_battle_details(battle, guild_name=None, alliance_name=None):
    """
    Função para mostrar detalhes de uma batalha específica
    Esta função mantém compatibilidade com o código antigo

    Args:
        battle: Dados da batalha
        guild_name: Nome da guild (opcional)
        alliance_name: Nome da aliança (opcional)
    """
    if guild_name is None:
        guild_name = GUILD_NAME

    # Chamamos o componente modularizado
    from components.battle_details import show_battle_details as component_show_battle_details
    component_show_battle_details(battle, guild_name, alliance_name)

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
                <span style="color: #F5B841; font-weight: 600;">⏱️ Status de Dados</span><br>
                Última atualização: <b>{last_update.strftime('%d/%m/%Y %H:%M')}</b><br>
                Próxima atualização: <b>{next_update.strftime('%d/%m/%Y %H:%M')}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🔄 Atualizar Dados Agora", type="primary"):
            with st.spinner("Buscando dados do scraper..."):
                try:
                    # Usar force_refresh=True para buscar dados diretamente do scraper
                    st.session_state['battles_data'] = get_battle_data(force_refresh=True)
                    from datetime import timezone
                    st.session_state['last_update'] = datetime.now(timezone.utc)
                    st.success("Dados atualizados com sucesso do scraper!")
                except Exception as e:
                    st.error(f"Falha ao atualizar dados: {str(e)}")
                    logging.error(f"Erro na atualização manual: {e}")
                    # Se houver erro, tenta carregar dados existentes
                    st.session_state['battles_data'] = get_battle_data()
                    st.warning("Usando dados locais devido a erro no scraper.")

    # Abas principais
    tabs = st.tabs(["📊 Visão Geral", "🏆 Ranking de Jogadores", "⚔️ Detalhes de Batalhas", "📈 Comparativos", "📋 Attendance"])

    # Container para filtros com estilo dourado da guild
    with st.container():
        st.markdown("""
        <div style="background-color: rgba(245, 184, 65, 0.15); padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid rgba(245, 184, 65, 0.3); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);">
            <h4 style="color: #F5B841; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 16px;">
                <span style="font-size: 16px;">⚙️</span> Filtros de Batalha
            </h4>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            min_players = st.slider(
                "Mínimo de jogadores por batalha",
                min_value=1,
                max_value=50,
                value=MIN_PLAYERS,
                step=1,
                key="min_players_slider"
            )
        
        with col2:
            days = st.slider(
                "Dias a considerar",
                min_value=1,
                max_value=30,
                value=7,
                step=1,
                key="days_slider"
            )

    # Filtrar batalhas
    battles_df = st.session_state['battles_data']
    filtered_battles = filter_battles_by_players(battles_df, min_players)
    recent_battles = get_recent_battles(filtered_battles, days)

    # Tab 1: Visão Geral
    with tabs[0]:
        if recent_battles.empty:
            st.warning("Nenhuma batalha encontrada com os filtros atuais.")
        else:
            show_guild_overview(recent_battles, GUILD_NAME, ALLIANCE_NAME)

    # Tab 2: Ranking de Jogadores
    with tabs[1]:
        if recent_battles.empty:
            st.warning("Nenhuma batalha encontrada com os filtros atuais.")
        else:
            show_player_rankings(recent_battles, GUILD_NAME)

    # Tab 3: Detalhes de Batalhas
    with tabs[2]:
        if recent_battles.empty:
            st.warning("Nenhuma batalha encontrada com os filtros atuais.")
        else:
            # Se uma batalha foi selecionada anteriormente
            if st.session_state['selected_battle'] is not None:
                battle = st.session_state['selected_battle']
                show_battle_details(battle, GUILD_NAME, ALLIANCE_NAME)

                if st.button("← Voltar para a lista de batalhas"):
                    st.session_state['selected_battle'] = None
                    st.rerun()
            else:
                # Lista de batalhas
                st.subheader("Selecione uma batalha para ver detalhes")

                for idx, battle in recent_battles.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                    with col1:
                        st.write(f"**Batalha #{battle['battle_id']}**")
                        st.caption(f"{battle['time'].strftime('%d/%m/%Y %H:%M')}")

                    with col2:
                        st.write(f"Kills: {battle['kills']}")

                    with col3:
                        st.write(f"Mortes: {battle['deaths']}")

                    with col4:
                        kd = battle['kills'] / max(1, battle['deaths'])
                        st.write(f"K/D: {kd:.2f}")

                    with col5:
                        if st.button("Detalhes", key=f"btn_{battle['battle_id']}"):
                            st.session_state['selected_battle'] = battle
                            st.rerun()

                    st.divider()

    # Tab 4: Comparativos
    with tabs[3]:
        if recent_battles.empty:
            st.warning("Nenhuma batalha encontrada com os filtros atuais.")
        else:
            show_comparison_tools(recent_battles, GUILD_NAME, ALLIANCE_NAME)
            
    # Tab 5: Attendance
    with tabs[4]:
        if recent_battles.empty:
            st.warning("Nenhuma batalha encontrada com os filtros atuais.")
        else:
            show_attendance_tracking(recent_battles, GUILD_NAME)

# Iniciar o app
if __name__ == "__main__":
    main()
