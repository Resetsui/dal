import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import format_number, create_kd_gauge

def show_battle_details(battle_data, guild_name, alliance_name):
    """Display detailed information about a specific battle"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(245, 184, 65, 0.15) 0%, rgba(0, 0, 0, 0) 100%);
         padding: 20px; border-radius: 12px; margin: 25px 0; 
         border-left: 4px solid #F5B841;">
        <h1 style="color: #F5B841; margin: 0; font-size: 32px;">🏆 Detalhes da Batalha</h1>
    </div>
    """, unsafe_allow_html=True)

    # Battle header with time
    battle_time = battle_data['time'].strftime('%d/%m/%Y %H:%M')
    st.markdown(f"""
    <div style="background-color: #2d2d42; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h2 style="color: #8be9fd; margin: 0; font-size: 24px;">⚔️ Batalha em {battle_time}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Verificar se os detalhes da batalha contêm as informações necessárias
    if 'details' not in battle_data or not isinstance(battle_data['details'], dict):
        st.error("Detalhes da batalha não encontrados ou em formato inválido")
        return

    battle_details = battle_data['details']

    # Verificar se o campo guilds existe nos detalhes
    if 'guilds' not in battle_details:
        st.error("Informações de guilds não encontradas nesta batalha")
        st.json(battle_details)  # Mostrar os detalhes disponíveis para debug
        return

    # Find our guild in the battle
    guild_stats = None
    enemy_guilds = {}
    alliance_guilds = {}
    guild_key = ''

    for guild, stats in battle_details['guilds'].items():
        if guild_name.lower() in guild.lower():
            guild_stats = stats
            guild_key = guild
        # Verificar se a guild é da aliança pela flag alliance, pelo nome de aliança ou pelo ID
        elif 'alliance' in stats and stats['alliance'] == True:
            alliance_guilds[guild] = stats
        elif 'alliance_name' in stats and stats['alliance_name'] == alliance_name:
            alliance_guilds[guild] = stats
            # Marcar como aliança se ainda não estiver marcada
            if 'alliance' not in stats:
                stats['alliance'] = True
        elif alliance_name and alliance_name.lower() in guild.lower():
            alliance_guilds[guild] = stats
            # Marcar como aliança se ainda não estiver marcada
            if 'alliance' not in stats:
                stats['alliance'] = True
        else:
            enemy_guilds[guild] = stats

    if not guild_stats:
        st.error(f"Guild '{guild_name}' not found in this battle")
        return

    # Calculate battle stats
    guild_kills = guild_stats['total_kills']
    guild_deaths = guild_stats['total_deaths']
    guild_fame = guild_stats['total_fame']
    guild_kd = guild_kills / max(1, guild_deaths)
    guild_players = len(guild_stats['players'])

    enemy_kills = sum(stats['total_kills'] for stats in enemy_guilds.values())
    enemy_deaths = sum(stats['total_deaths'] for stats in enemy_guilds.values())
    enemy_fame = sum(stats['total_fame'] for stats in enemy_guilds.values())
    enemy_kd = enemy_kills / max(1, enemy_deaths)

    # Melhorar a contagem de jogadores inimigos (preferindo o player_count se disponível)
    enemy_players = 0
    for guild, stats in enemy_guilds.items():
        if 'player_count' in stats:
            enemy_players += stats['player_count']
        else:
            enemy_players += len(stats['players'])

    alliance_kills = sum(stats['total_kills'] for stats in alliance_guilds.values())
    alliance_deaths = sum(stats['total_deaths'] for stats in alliance_guilds.values())
    alliance_fame = sum(stats['total_fame'] for stats in alliance_guilds.values())

    # Melhorar a contagem de jogadores da aliança (preferindo o player_count se disponível)
    alliance_players = 0
    for guild, stats in alliance_guilds.items():
        if 'player_count' in stats:
            alliance_players += stats['player_count']
        else:
            alliance_players += len(stats['players'])

    # Determine victory
    friendly_kd = (guild_kills + alliance_kills) / max(1, guild_deaths + alliance_deaths)
    victory = friendly_kd > enemy_kd

    # Painel de resumo da batalha
    outcome = "VITÓRIA" if victory else "DERROTA"
    outcome_color = "#50fa7b" if victory else "#ff5555"

    st.markdown(f"""
    <div style="background-color: #7E57C220; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">Detalhes da Batalha</h3>
                <p>Data: {battle_time}</p>
            </div>
            <div style="text-align: right;">
                <h2 style="color: {outcome_color}; margin: 0;">{outcome}</h2>
                <p>K/D: {friendly_kd:.2f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Battle overview
    st.markdown(f"""
    <div style="background-color: #2d2d42; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        <h2 style="text-align: center; color: {'#50fa7b' if victory else '#ff5555'}; font-size: 28px; margin-bottom: 30px;">
            {'VITÓRIA' if victory else 'DERROTA'}
        </h2>
        <div style="display: flex; justify-content: space-between; text-align: center; gap: 20px;">
            <div style="flex: 1; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 4px solid #bd93f9;">
                <h3 style="color: #bd93f9; margin-bottom: 20px; font-size: 20px;">{guild_name}</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="background: rgba(189,147,249,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Players</div>
                        <div style="font-size: 18px; font-weight: 500;">{guild_players}</div>
                    </div>
                    <div style="background: rgba(189,147,249,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">K/D</div>
                        <div style="font-size: 18px; font-weight: 500;">{guild_kd:.2f}</div>
                    </div>
                    <div style="background: rgba(189,147,249,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Kills</div>
                        <div style="font-size: 18px; font-weight: 500;">{guild_kills}</div>
                    </div>
                    <div style="background: rgba(189,147,249,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Deaths</div>
                        <div style="font-size: 18px; font-weight: 500;">{guild_deaths}</div>
                    </div>
                    <div style="background: rgba(189,147,249,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Fame</div>
                        <div style="font-size: 18px; font-weight: 500;">{format_number(guild_fame)}</div>
                    </div>
                </div>
            </div>
            <div style="flex: 1; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 4px solid #8be9fd;">
                <h3 style="color: #8be9fd; margin-bottom: 20px; font-size: 20px;">Alliance</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="background: rgba(139,233,253,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Players</div>
                        <div style="font-size: 18px; font-weight: 500;">{alliance_players}</div>
                    </div>
                    <div style="background: rgba(139,233,253,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">K/D</div>
                        <div style="font-size: 18px; font-weight: 500;">{(alliance_kills / max(1, alliance_deaths)):.2f}</div>
                    </div>
                    <div style="background: rgba(139,233,253,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Kills</div>
                        <div style="font-size: 18px; font-weight: 500;">{alliance_kills}</div>
                    </div>
                    <div style="background: rgba(139,233,253,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Deaths</div>
                        <div style="font-size: 18px; font-weight: 500;">{alliance_deaths}</div>
                    </div>
                    <div style="background: rgba(139,233,253,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #8be9fd; font-size: 14px; margin-bottom: 4px;">Fame</div>
                        <div style="font-size: 18px; font-weight: 500;">{format_number(alliance_fame)}</div>
                    </div>
                </div>
            </div>
            <div style="flex: 1; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 4px solid #ff5555;">
                <h3 style="color: #ff5555; margin-bottom: 20px; font-size: 20px;">Enemies</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="background: rgba(255,85,85,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #ff5555; font-size: 14px; margin-bottom: 4px;">Players</div>
                        <div style="font-size: 18px; font-weight: 500;">{enemy_players}</div>
                    </div>
                    <div style="background: rgba(255,85,85,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #ff5555; font-size: 14px; margin-bottom: 4px;">K/D</div>
                        <div style="font-size: 18px; font-weight: 500;">{enemy_kd:.2f}</div>
                    </div>
                    <div style="background: rgba(255,85,85,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #ff5555; font-size: 14px; margin-bottom: 4px;">Kills</div>
                        <div style="font-size: 18px; font-weight: 500;">{enemy_kills}</div>
                    </div>
                    <div style="background: rgba(255,85,85,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #ff5555; font-size: 14px; margin-bottom: 4px;">Deaths</div>
                        <div style="font-size: 18px; font-weight: 500;">{enemy_deaths}</div>
                    </div>
                    <div style="background: rgba(255,85,85,0.1); padding: 12px; border-radius: 8px;">
                        <div style="color: #ff5555; font-size: 14px; margin-bottom: 4px;">Fame</div>
                        <div style="font-size: 18px; font-weight: 500;">{format_number(enemy_fame)}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Guild KD gauge chart
    st.plotly_chart(create_kd_gauge(guild_kills, guild_deaths), use_container_width=True)

    # Calculate and display death costs
    death_cost_per_player = 1729507.6
    total_death_cost = 0

    # Calculate total death cost
    if guild_stats and guild_key:
        for player in guild_stats['players']:
            total_death_cost += player['deaths'] * death_cost_per_player
        
        # Convert to millions and format with 3 decimal places
        total_death_cost_m = f"{total_death_cost / 1000000:.3f}"
        
        st.markdown(f"""
        <div style="background-color: #2d2d42; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #ff5555; margin-bottom: 15px;">💰 Custo Total de Mortes</h3>
            <h2 style="color: #ff5555; font-size: 24px;">{total_death_cost_m}M Silver</h2>
        </div>
        """, unsafe_allow_html=True)

    # Player performance
    st.subheader("🎮 Player Performance")

    # Create DataFrame for players
    players_df = pd.DataFrame(guild_stats['players'])

    # Add KD ratio
    if not players_df.empty:
        players_df['kd_ratio'] = players_df['kills'] / players_df['deaths'].replace(0, 1)

        # Sort by kills
        players_df = players_df.sort_values('kills', ascending=False)

        # Top players
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Top Killers")
            top_killers = players_df.head(3)
            for i, (_, player) in enumerate(top_killers.iterrows()):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.markdown(f"""
<div style="background-color: #2d2d42; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
    <h4>{medal} {player['name']}</h4>
    <div style="display: flex; justify-content: space-between;">
        <div>Kills: {player['kills']}</div>
        <div>Deaths: {player['deaths']}</div>
        <div>K/D: {'{:.2f}'.format(player['kd_ratio'])}</div>
    </div>
</div>""", unsafe_allow_html=True)

        with col2:
            st.subheader("💀 Most Deaths")
            top_deaths = players_df.sort_values('deaths', ascending=False).head(3)
            for i, (_, player) in enumerate(top_deaths.iterrows()):
                medal = "💀" if i == 0 else "☠️" if i == 1 else "👻"
                st.markdown(f"""
                <div style="background-color: #2d2d42; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>{medal} {player['name']}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Deaths: {player['deaths']}</div>
                        <div>Kills: {player['kills']}</div>
                        <div>K/D: {'{:.2f}'.format(player['kd_ratio'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Player performance charts
        st.subheader("📊 Player Statistics")

        # Create kills chart
        fig_kills = px.bar(
            players_df.head(10),
            x='name',
            y='kills',
            title="Top 10 Players by Kills",
            color='kills',
            color_continuous_scale=px.colors.sequential.Viridis
        )

        fig_kills.update_layout(
            xaxis_title="Player",
            yaxis_title="Kills",
            paper_bgcolor="#2d2d42",
            plot_bgcolor="#1e1e2e",
            font=dict(color="#f8f8f2")
        )

        st.plotly_chart(fig_kills, use_container_width=True)

        # Create KD ratio chart
        fig_kd = px.bar(
            players_df.sort_values('kd_ratio', ascending=False).head(10),
            x='name',
            y='kd_ratio',
            title="Top 10 Players by K/D Ratio",
            color='kd_ratio',
            color_continuous_scale=px.colors.sequential.Viridis
        )

        fig_kd.update_layout(
            xaxis_title="Player",
            yaxis_title="K/D Ratio",
            paper_bgcolor="#2d2d42",
            plot_bgcolor="#1e1e2e",
            font=dict(color="#f8f8f2")
        )

        st.plotly_chart(fig_kd, use_container_width=True)

    # Participating Guilds
    st.subheader("⚔️ Participating Guilds")

    # Create guild comparison data
    guild_comparison = []

    # Add our guild
    guild_comparison.append({
        'name': guild_key,
        'players': guild_players,
        'kills': guild_kills,
        'deaths': guild_deaths,
        'kd_ratio': guild_kd,
        'fame': guild_fame,
        'type': 'Guild'
    })

    # Add alliance guilds
    for name, stats in alliance_guilds.items():
        alliance_kd = stats['total_kills'] / max(1, stats['total_deaths'])
        # Usar player_count se disponível, caso contrário usar o comprimento da lista de jogadores
        player_count = stats.get('player_count', len(stats['players']))
        guild_comparison.append({
            'name': name,
            'players': player_count,
            'kills': stats['total_kills'],
            'deaths': stats['total_deaths'],
            'kd_ratio': alliance_kd,
            'fame': stats['total_fame'],
            'type': 'Alliance'
        })

    # Add enemy guilds
    for name, stats in enemy_guilds.items():
        enemy_guild_kd = stats['total_kills'] / max(1, stats['total_deaths'])
        # Usar player_count se disponível, caso contrário usar o comprimento da lista de jogadores
        player_count = stats.get('player_count', len(stats['players']))
        guild_comparison.append({
            'name': name,
            'players': player_count,
            'kills': stats['total_kills'],
            'deaths': stats['total_deaths'],
            'kd_ratio': enemy_guild_kd,
            'fame': stats['total_fame'],
            'type': 'Enemy'
        })

    # Create DataFrame
    guild_df = pd.DataFrame(guild_comparison)

    # Exibindo detalhes das guilds aliadas em cards
    st.subheader("🛡️ Aliados na Batalha")

    # Filtrando apenas as guilds da aliança
    alliance_df = guild_df[guild_df['type'] == 'Alliance']

    if not alliance_df.empty:
        # Ordenando por número de jogadores para destacar os aliados mais relevantes
        alliance_df = alliance_df.sort_values('players', ascending=False)

        # Criando três colunas para exibir os cards
        cols = st.columns(3)

        # Exibindo os cards das guilds da aliança
        for i, (_, ally) in enumerate(alliance_df.iterrows()):
            with cols[i % 3]:
                kd_color = "#50fa7b" if ally['kd_ratio'] >= 1.0 else "#ff5555"
                st.markdown(f"""
                <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 5px solid #8be9fd;">
                    <h4 style="margin-top: 0;">{ally['name']}</h4>
                    <div style="display: flex; flex-direction: column; gap: 5px;">
                        <div><b>👥 Players:</b> {ally['players']}</div>
                        <div><b>⚔️ Kills:</b> {ally['kills']}</div>
                        <div><b>💀 Deaths:</b> {ally['deaths']}</div>
                        <div><b>K/D:</b> <span style="color: {kd_color};">{ally['kd_ratio']:.2f}</span></div>
                        <div><b>🏆 Fame:</b> {format_number(ally['fame'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Limitar a exibição a 6 aliados para não sobrecarregar a interface
            if i >= 5:
                st.markdown(f"**+{len(alliance_df) - 6} outros aliados nesta batalha**")
                break
    else:
        st.info("Nenhum aliado encontrado nesta batalha.")

    # Exibindo detalhes dos inimigos em cards
    st.subheader("🔍 Detalhes dos Oponentes")

    # Filtrando apenas os inimigos
    enemy_df = guild_df[guild_df['type'] == 'Enemy']

    if not enemy_df.empty:
        # Ordenando por número de jogadores para destacar os oponentes mais relevantes
        enemy_df = enemy_df.sort_values('players', ascending=False)

        # Criando três colunas para exibir os cards
        cols = st.columns(3)

        # Exibindo os cards dos inimigos
        for i, (_, enemy) in enumerate(enemy_df.iterrows()):
            with cols[i % 3]:
                kd_color = "#50fa7b" if enemy['kd_ratio'] >= 1.0 else "#ff5555"
                st.markdown(f"""
                <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 5px solid #ff5555;">
                    <h4 style="margin-top: 0;">{enemy['name']}</h4>
                    <div style="display: flex; flex-direction: column; gap: 5px;">
                        <div><b>👥 Players:</b> {enemy['players']}</div>
                        <div><b>⚔️ Kills:</b> {enemy['kills']}</div>
                        <div><b>💀 Deaths:</b> {enemy['deaths']}</div>
                        <div><b>K/D:</b> <span style="color: {kd_color};">{enemy['kd_ratio']:.2f}</span></div>
                        <div><b>🏆 Fame:</b> {format_number(enemy['fame'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Limitar a exibição a 6 inimigos para não sobrecarregar a interface
            if i >= 5:
                st.markdown(f"**+{len(enemy_df) - 6} outros oponentes nesta batalha**")
                break
    else:
        st.info("Nenhum oponente encontrado nesta batalha.")

    # Create guild comparison chart
    st.subheader("📊 Comparativo de Guilds")

    fig_guild = px.bar(
        guild_df,
        x='name',
        y='kills',
        color='type',
        title="Comparativo de Kills por Guild",
        color_discrete_map={
            'Guild': '#9b59b6',
            'Alliance': '#8be9fd',
            'Enemy': '#ff5555'
        },
        hover_data=['players', 'deaths', 'kd_ratio']
    )

    fig_guild.update_layout(
        xaxis_title="Guild",
        yaxis_title="Kills",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )

    st.plotly_chart(fig_guild, use_container_width=True)

    # Guild KD ratio chart
    fig_guild_kd = px.bar(
        guild_df,
        x='name',
        y='kd_ratio',
        color='type',
        title="Comparativo de K/D Ratio por Guild",
        color_discrete_map={
            'Guild': '#9b59b6',
            'Alliance': '#8be9fd',
            'Enemy': '#ff5555'
        },
        hover_data=['players', 'kills', 'deaths']
    )

    fig_guild_kd.update_layout(
        xaxis_title="Guild",
        yaxis_title="K/D Ratio",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )

    st.plotly_chart(fig_guild_kd, use_container_width=True)

    # Players comparison chart
    fig_players = px.bar(
        guild_df,
        x='name',
        y='players',
        color='type',
        title="Comparativo de Número de Jogadores por Guild",
        color_discrete_map={
            'Guild': '#9b59b6',
            'Alliance': '#8be9fd',
            'Enemy': '#ff5555'
        },
        hover_data=['kills', 'deaths', 'kd_ratio']
    )

    fig_players.update_layout(
        xaxis_title="Guild",
        yaxis_title="Número de Jogadores",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )

    st.plotly_chart(fig_players, use_container_width=True)