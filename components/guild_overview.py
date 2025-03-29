import streamlit as st
import pandas as pd
import plotly.express as px
from utils import format_number, create_kd_gauge

def show_guild_overview(battles_df, guild_name, alliance_name=None):
    st.header("📊 Visão Geral da Guild")

    if battles_df.empty:
        st.warning("Nenhum dado de batalha disponível.")
        return

    # Calcular estatísticas gerais
    total_battles = len(battles_df)
    total_players = set()
    total_kills = 0
    total_deaths = 0
    victories = 0

    for _, battle in battles_df.iterrows():
        details = battle['details']
        if guild_name in details['guilds']:
            guild_stats = details['guilds'][guild_name]
            total_kills += guild_stats['total_kills']
            total_deaths += guild_stats['total_deaths']

            # Contar jogadores únicos
            for player in guild_stats['players']:
                total_players.add(player['name'])

            # Verificar vitória
            guild_kd = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
            enemy_kills = sum(
                stats['total_kills'] 
                for g, stats in details['guilds'].items() 
                if g != guild_name
            )
            enemy_deaths = sum(
                stats['total_deaths']
                for g, stats in details['guilds'].items()
                if g != guild_name
            )
            enemy_kd = enemy_kills / max(1, enemy_deaths)

            if guild_kd > enemy_kd:
                victories += 1

    # Métricas principais
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0;">
        <div style="background: rgba(189,147,249,0.1); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 14px; color: #8be9fd; margin-bottom: 10px;">Total de Batalhas</div>
            <div style="font-size: 24px; font-weight: bold;">{}</div>
            <div style="font-size: 14px; color: #8be9fd; margin: 15px 0 10px;">Jogadores Ativos</div>
            <div style="font-size: 24px; font-weight: bold;">{}</div>
        </div>
        <div style="background: rgba(189,147,249,0.1); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 14px; color: #8be9fd; margin-bottom: 10px;">Batalhas Vencidas</div>
            <div style="font-size: 24px; font-weight: bold;">{}</div>
            <div style="font-size: 14px; color: #8be9fd; margin: 15px 0 10px;">Taxa de Vitória</div>
            <div style="font-size: 24px; font-weight: bold;">{:.1f}%</div>
        </div>
        <div style="background: rgba(189,147,249,0.1); padding: 20px; border-radius: 12px; text-align: center;">
            <div style="font-size: 14px; color: #8be9fd; margin-bottom: 10px;">K/D Geral</div>
            <div style="font-size: 24px; font-weight: bold;">{:.2f}</div>
            <div style="font-size: 14px; color: #8be9fd; margin: 15px 0 10px;">Total de Kills</div>
            <div style="font-size: 24px; font-weight: bold;">{}</div>
        </div>
    </div>
    """.format(
        total_battles,
        len(total_players),
        victories,
        (victories / total_battles * 100) if total_battles > 0 else 0,
        total_kills / max(1, total_deaths),
        total_kills
    ), unsafe_allow_html=True)

    # Top Performers
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(245, 184, 65, 0.15) 0%, rgba(0, 0, 0, 0) 100%);
         padding: 20px; border-radius: 12px; margin: 25px 0; 
         border-left: 4px solid #F5B841;">
        <h2 style="color: #F5B841; margin: 0; font-size: 24px;">🏆 Top Performers</h2>
    </div>
    """, unsafe_allow_html=True)

    # Processar dados dos jogadores
    players_data = {}
    for _, battle in battles_df.iterrows():
        details = battle['details']
        if guild_name in details['guilds']:
            for player in details['guilds'][guild_name]['players']:
                name = player['name']
                if name not in players_data:
                    players_data[name] = {
                        'kills': 0,
                        'deaths': 0,
                        'battles': 0
                    }
                players_data[name]['kills'] += player['kills']
                players_data[name]['deaths'] += player['deaths']
                players_data[name]['battles'] += 1

    # Calcular K/D e encontrar top performers
    for name, data in players_data.items():
        data['kd_ratio'] = data['kills'] / max(1, data['deaths'])

    # Criar DataFrame e ordenar
    players_df = pd.DataFrame.from_dict(players_data, orient='index')

    # Top Killer
    kill_master = players_df.nlargest(1, 'kills').iloc[0]
    kill_master_name = kill_master.name

    # Death Champion
    death_champion = players_df.nlargest(1, 'deaths').iloc[0]
    death_champion_name = death_champion.name

    # MVP (melhor K/D com mínimo de batalhas)
    mvp = players_df[players_df['battles'] >= 3].nlargest(1, 'kd_ratio').iloc[0]
    mvp_name = mvp.name

    # Most Active
    most_active = players_df.nlargest(1, 'battles').iloc[0]
    most_active_name = most_active.name

    # Exibir cards dos top performers
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(80, 250, 123, 0.2);">
            <h3 style="color: #50fa7b; margin-bottom: 10px;">🎯 Mestre das Kills</h3>
            <h2 style="color: white; margin-bottom: 15px;">{kill_master_name}</h2>
            <p>Total de Kills: {int(kill_master['kills'])}</p>
            <p>K/D Ratio: {kill_master['kd_ratio']:.2f}</p>
            <p>Batalhas: {int(kill_master['battles'])}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(189, 147, 249, 0.2);">
            <h3 style="color: #bd93f9; margin-bottom: 10px;">🏆 MVP</h3>
            <h2 style="color: white; margin-bottom: 15px;">{mvp_name}</h2>
            <p>K/D Ratio: {mvp['kd_ratio']:.2f}</p>
            <p>Kills: {int(mvp['kills'])}</p>
            <p>Deaths: {int(mvp['deaths'])}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 85, 85, 0.2);">
            <h3 style="color: #ff5555; margin-bottom: 10px;">💀 Campeão de Mortes</h3>
            <h2 style="color: white; margin-bottom: 15px;">{death_champion_name}</h2>
            <p>Total de Mortes: {int(death_champion['deaths'])}</p>
            <p>Kills: {int(death_champion['kills'])}</p>
            <p>K/D Ratio: {death_champion['kd_ratio']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 121, 198, 0.2);">
            <h3 style="color: #ff79c6; margin-bottom: 10px;">⚔️ Mais Ativo</h3>
            <h2 style="color: white; margin-bottom: 15px;">{most_active_name}</h2>
            <p>Batalhas: {int(most_active['battles'])}</p>
            <p>Total de Kills: {int(most_active['kills'])}</p>
            <p>Total de Mortes: {int(most_active['deaths'])}</p>
        </div>
        """, unsafe_allow_html=True)

    # Seção de Batalhas Recentes
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(245, 184, 65, 0.15) 0%, rgba(0, 0, 0, 0) 100%);
         padding: 20px; border-radius: 12px; margin: 25px 0; 
         border-left: 4px solid #F5B841;">
        <h2 style="color: #F5B841; margin: 0; font-size: 24px;">⚔️ Batalhas Recentes</h2>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar as últimas 5 batalhas
    recent_battles = battles_df.head(5)

    for _, battle in recent_battles.iterrows():
        battle_time = battle['time'].strftime('%d/%m/%Y %H:%M')
        details = battle['details']
        
        guild_stats = None
        enemy_guilds = []
        
        # Identificar nossa guild e as guilds inimigas
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_stats = stats
            else:
                enemy_guilds.append(guild)
                
        if guild_stats:
            guild_kd = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
            enemy_names = " | ".join(enemy_guilds)
            
            st.markdown(f"""
            <div style="background: rgba(30, 30, 40, 0.6); padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #BD93F9;">⚔️ {battle_time}</span>
                        <span style="color: #FF5555; margin-left: 10px;">vs {enemy_names}</span>
                    </div>
                    <div>
                        <span style="color: #50FA7B;">K/D: {guild_kd:.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            enemy_kills = sum(
                stats['total_kills'] 
                for g, stats in details['guilds'].items() 
                if g != guild_name
            )
            enemy_deaths = sum(
                stats['total_deaths']
                for g, stats in details['guilds'].items() 
                if g != guild_name
            )
            enemy_kd = enemy_kills / max(1, enemy_deaths)

            victory = guild_kd > enemy_kd
            result_color = "#50fa7b" if victory else "#ff5555"
            result_text = "VITÓRIA" if victory else "DERROTA"

            st.markdown(f"""
            <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>{battle_time}</div>
                    <div style="color: {result_color}; font-weight: bold;">{result_text}</div>
                </div>
                <div style="margin-top: 10px;">
                    <div>Kills: {guild_stats['total_kills']} | Deaths: {guild_stats['total_deaths']} | K/D: {guild_kd:.2f}</div>
                    <div>Jogadores: {len(guild_stats['players'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)