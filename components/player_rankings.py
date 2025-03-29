import streamlit as st
import pandas as pd
import plotly.express as px
from utils import create_player_chart

def show_player_rankings(battles_df, guild_name):
    """Display player rankings with various metrics"""
    st.header("👑 Player Rankings")

    # Informações de destaque dos jogadores
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"""
        <div style="background-color: #7E57C220; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #7E57C2; margin: 0;">Ranking de Jogadores</h3>
            <p>Análise detalhada da performance individual dos membros de <strong>{guild_name}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Pequena dica explicativa
        st.info("""
        **Como usar os rankings:**
        - Selecione o mínimo de batalhas para filtrar jogadores ocasionais
        - Compare diferentes métricas para avaliar o desempenho
        """)

    if battles_df.empty:
        st.warning("No battle data available for player rankings.")
        return

    # Process player data from battles
    players_data = {}

    for _, battle in battles_df.iterrows():
        details = battle['details']

        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                for player in stats['players']:
                    name = player['name']
                    if name not in players_data:
                        players_data[name] = {
                            'name': name,
                            'kills': 0,
                            'deaths': 0,
                            'fame': 0,
                            'battles': 0,
                            'avg_kills': 0,
                            'avg_deaths': 0
                        }

                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1

    # Calculate derived metrics
    for name, data in players_data.items():
        battles = max(1, data['battles'])
        data['avg_kills'] = data['kills'] / battles
        data['avg_deaths'] = data['deaths'] / battles
        data['kd_ratio'] = data['kills'] / max(1, data['deaths'])

    # Convert to DataFrame
    players_df = pd.DataFrame(list(players_data.values()))

    if players_df.empty:
        st.warning("No player data available.")
        return

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        min_battles = st.slider("Minimum Battles", 1, 10, 1)

    with col2:
        sort_by = st.selectbox(
            "Sort By",
            options=["kills", "deaths", "kd_ratio", "fame", "battles", "avg_kills", "avg_deaths"],
            format_func=lambda x: {
                'kills': 'Total Kills',
                'deaths': 'Total Deaths',
                'kd_ratio': 'K/D Ratio',
                'fame': 'Fame',
                'battles': 'Battles Participated',
                'avg_kills': 'Average Kills per Battle',
                'avg_deaths': 'Average Deaths per Battle'
            }[x]
        )

    # Filter and sort players
    filtered_players = players_df[players_df['battles'] >= min_battles].copy()
    filtered_players = filtered_players.sort_values(sort_by, ascending=False)

    if filtered_players.empty:
        st.warning(f"No players found with at least {min_battles} battles.")
        return

    # Display player rankings
    st.subheader(f"Rankings by {sort_by.replace('_', ' ').title()}")

    # Create chart
    fig = create_player_chart(filtered_players.to_dict('records'), sort_by)
    st.plotly_chart(fig, use_container_width=True)

    # Add silver cost calculation
    death_cost_per_player = 1729507.6
    filtered_players['silver_cost'] = filtered_players['deaths'] * death_cost_per_player
    filtered_players['silver_cost_m'] = (filtered_players['silver_cost'] / 1000000).round(3)

    # Create silver cost chart
    st.subheader("💰 Custo em Prata por Jogador")
    
    # Prepare data for horizontal bar chart
    cost_df = filtered_players.sort_values('silver_cost_m', ascending=True).tail(10)
    
    fig_silver = px.bar(
        cost_df,
        x='silver_cost_m',
        y='name',
        orientation='h',
        title="Top 10 Jogadores - Custo em Prata",
        text=cost_df['silver_cost_m'].apply(lambda x: f'{x:.3f}M'),
        color='silver_cost_m',
        color_continuous_scale=['#FF9B9B', '#FF5555'],
        hover_data=None,
        custom_data=['name', 'silver_cost_m']
    )
    
    # Remove color scale bar
    fig_silver.update_coloraxes(showscale=False)
    
    fig_silver.update_traces(
        hovertemplate='Jogador: %{customdata[0]}<br>Custo: %{x:.3f}M Silver<extra></extra>'
    )

    fig_silver.update_layout(
        xaxis_title="Milhões de Prata",
        yaxis_title="Jogador",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2"),
        showlegend=False,
        height=400,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    # Update text position and format
    fig_silver.update_traces(
        textposition='outside',
        textfont=dict(size=14)
    )

    st.plotly_chart(fig_silver, use_container_width=True)

    # Display detailed player table
    st.subheader("Detailed Player Statistics")

    # Format the DataFrame for display
    display_df = filtered_players[['name', 'kills', 'deaths', 'kd_ratio', 'fame', 'battles', 'avg_kills', 'avg_deaths', 'silver_cost_m']].copy()

    # Format the columns
    display_df['kd_ratio'] = display_df['kd_ratio'].round(2)
    display_df['avg_kills'] = display_df['avg_kills'].round(2)
    display_df['avg_deaths'] = display_df['avg_deaths'].round(2)

    # Rename columns for better display
    display_df.columns = [
        'Player',
        'Kills',
        'Deaths',
        'K/D Ratio',
        'Fame',
        'Battles',
        'Avg Kills',
        'Avg Deaths',
        'Custo (M Silver)'
    ]

    # Display the table
    st.markdown("""
        <style>
        .dataframe {
            font-family: 'Inter', sans-serif;
            border-radius: 10px;
            overflow: hidden;
            background: rgba(30, 30, 40, 0.7);
        }
        .dataframe th {
            background: rgba(40, 40, 50, 0.9) !important;
            color: #fff !important;
            font-weight: 600 !important;
        }
        .dataframe td {
            font-size: 14px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500
    )

    # Top performer highlights
    st.subheader("🏆 Top Performers")

    col1, col2 = st.columns(2)

    with col1:
        # Top killer
        top_killer = filtered_players.loc[filtered_players['kills'].idxmax()]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(30, 30, 40, 0.8) 0%, rgba(20, 20, 30, 0.9) 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(80, 250, 123, 0.3); position: relative; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: #50fa7b;"></div>
            <h3 style="color: #50fa7b; margin: 0 0 10px 0; font-size: 20px;">🎯 Kill Master</h3>
            <h2 style="color: white; margin: 0 0 15px 0; font-size: 28px;">{top_killer['name']}</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: rgba(80, 250, 123, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #50fa7b;">{top_killer['kills']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Total Kills</div>
                </div>
                <div style="background: rgba(80, 250, 123, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #50fa7b;">{top_killer['kd_ratio']:.2f}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">K/D Ratio</div>
                </div>
                <div style="background: rgba(80, 250, 123, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #50fa7b;">{top_killer['battles']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Battles</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Most deaths
        top_deaths = filtered_players.loc[filtered_players['deaths'].idxmax()]
        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 85, 85, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: #ff5555;"></div>
            <h3 style="color: #ff5555; margin: 0 0 10px 0; font-size: 20px;">💀 Death Champion</h3>
            <h2 style="color: white; margin: 0 0 15px 0; font-size: 28px;">{top_deaths['name']}</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: rgba(255, 85, 85, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff5555;">{top_deaths['deaths']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Total Deaths</div>
                </div>
                <div style="background: rgba(255, 85, 85, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff5555;">{top_deaths['kills']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Kills</div>
                </div>
                <div style="background: rgba(255, 85, 85, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff5555;">{top_deaths['kd_ratio']:.2f}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">K/D Ratio</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        # Best K/D (minimum 3 battles)
        kd_players = filtered_players[filtered_players['battles'] >= 3]
        if not kd_players.empty:
            best_kd = kd_players.loc[kd_players['kd_ratio'].idxmax()]
            st.markdown(f"""
            <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(189, 147, 249, 0.2); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: #bd93f9;"></div>
                <h3 style="color: #bd93f9; margin: 0 0 10px 0; font-size: 20px;">🏆 MVP</h3>
                <h2 style="color: white; margin: 0 0 15px 0; font-size: 28px;">{best_kd['name']}</h2>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    <div style="background: rgba(189, 147, 249, 0.1); padding: 10px; border-radius: 8px;">
                        <div style="font-size: 24px; color: #bd93f9;">{best_kd['kd_ratio']:.2f}</div>
                        <div style="color: #8BE9FD; font-size: 12px;">K/D Ratio</div>
                    </div>
                    <div style="background: rgba(189, 147, 249, 0.1); padding: 10px; border-radius: 8px;">
                        <div style="font-size: 24px; color: #bd93f9;">{best_kd['kills']}</div>
                        <div style="color: #8BE9FD; font-size: 12px;">Kills</div>
                    </div>
                    <div style="background: rgba(189, 147, 249, 0.1); padding: 10px; border-radius: 8px;">
                        <div style="font-size: 24px; color: #bd93f9;">{best_kd['deaths']}</div>
                        <div style="color: #8BE9FD; font-size: 12px;">Deaths</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        # Most active
        most_active = filtered_players.loc[filtered_players['battles'].idxmax()]
        st.markdown(f"""
        <div style="background: rgba(30, 30, 40, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 121, 198, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: #ff79c6;"></div>
            <h3 style="color: #ff79c6; margin: 0 0 10px 0; font-size: 20px;">⚔️ Most Active</h3>
            <h2 style="color: white; margin: 0 0 15px 0; font-size: 28px;">{most_active['name']}</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: rgba(255, 121, 198, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff79c6;">{most_active['battles']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Battles</div>
                </div>
                <div style="background: rgba(255, 121, 198, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff79c6;">{most_active['kills']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Total Kills</div>
                </div>
                <div style="background: rgba(255, 121, 198, 0.1); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 24px; color: #ff79c6;">{most_active['deaths']}</div>
                    <div style="color: #8BE9FD; font-size: 12px;">Total Deaths</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Player efficiency analysis
    st.subheader("📊 Análise de Eficiência dos Jogadores")

    # Calculate efficiency metrics
    filtered_players['kills_per_battle'] = (filtered_players['kills'] / filtered_players['battles']).round(2)
    filtered_players['deaths_per_battle'] = (filtered_players['deaths'] / filtered_players['battles']).round(2)
    
    # Nova fórmula de eficiência
    filtered_players['efficiency_score'] = (
        (filtered_players['kills_per_battle'] * 35) +  # Peso maior para kills por batalha
        (filtered_players['kd_ratio'] * 25) +          # K/D ratio importante mas não dominante
        (10 * (1 - (filtered_players['deaths_per_battle'] / filtered_players['deaths_per_battle'].max()))) + # Bônus por menos mortes
        (filtered_players['battles'] * 2)              # Bônus por participação
    ).round(2)

    # Normalizar score para 0-100
    max_score = filtered_players['efficiency_score'].max()
    filtered_players['efficiency_score'] = ((filtered_players['efficiency_score'] / max_score) * 100).round(1)
    
    # Sort by efficiency score
    efficiency_df = filtered_players.sort_values('efficiency_score', ascending=False)

    st.markdown("""
    ### 🎯 Sistema de Pontuação de Eficiência
    
    O score é calculado considerando:
    - **Agressividade** (35%): Kills por batalha
    - **Consistência** (25%): Razão K/D
    - **Sobrevivência** (20%): Taxa de mortes comparada
    - **Participação** (20%): Número de batalhas
    
    Score final é normalizado para escala 0-100
    """)

    # Create horizontal bar chart for efficiency scores
    fig = px.bar(
        efficiency_df.head(10),
        y='name',
        x='efficiency_score',
        orientation='h',
        color='efficiency_score',
        color_continuous_scale='viridis',
        title="🏆 Top 10 Jogadores por Eficiência",
        template="plotly_dark",
        hover_data={
            'name': True,
            'efficiency_score': ':.1f',
            'kills_per_battle': ':.1f',
            'kd_ratio': ':.2f',
            'battles': True
        },
        labels={
            'name': 'Jogador',
            'efficiency_score': 'Score de Eficiência',
            'kills_per_battle': 'Kills/Batalha',
            'kd_ratio': 'K/D',
            'battles': 'Batalhas'
        }
    )

    # Add diagonal line for K/D = 1
    max_val = max(filtered_players['kills'].max(), filtered_players['deaths'].max())
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=max_val,
        y1=max_val,
        line=dict(color="white", width=1, dash="dash"),
        name="K/D = 1"
    )

    fig.update_layout(
        xaxis_title="Score de Eficiência",
        yaxis_title="Jogador",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2"),
        height=400,
        bargap=0.1,
        margin=dict(l=100, r=20, t=30, b=40),
        yaxis=dict(
            automargin=True,
            tickmode='linear'
        ),
        xaxis=dict(
            range=[0, 105]  # Ajusta o zoom do eixo X para mostrar até 105 (considerando labels)
        )
    )

    # Improve hover information
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
        "Score: %{x:.2f}<br>" +
        "Kills: %{customdata[0]}<br>" +
        "Mortes: %{customdata[1]}<br>" +
        "Batalhas: %{customdata[2]}<br>" +
        "K/D: %{customdata[3]:.2f}<br>" +
        "<extra></extra>"
    )

    # Add value labels to the bars
    fig.update_traces(texttemplate='%{x:.2f}', textposition='outside')

    st.plotly_chart(fig, use_container_width=True)