import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import create_guild_comparison_chart

def show_comparison_tools(battles_df, guild_name, alliance_name):
    """Display tools to compare guild performance with enemies"""
    st.header("🔍 Guild Comparison Tools")
    
    # Cabeçalho com destaque visual para a guild
    st.markdown(f"""
    <div style="background-color: #7E57C220; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #7E57C2; margin: 0;">Análise Comparativa - {guild_name}</h3>
        <p>Comparação detalhada de performance em batalhas</p>
    </div>
    """, unsafe_allow_html=True)
    
    if battles_df.empty:
        st.warning("No battle data available for comparison.")
        return
    
    # Process guild and enemy data from battles
    guild_stats = {
        'name': guild_name,  # Adicionar o nome da guild para o gráfico
        'total_kills': 0,
        'total_deaths': 0,
        'total_fame': 0,
        'battles': 0,
        'wins': 0
    }
    
    enemy_guilds = {}
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        guild_data = None
        enemies_data = {}
        
        # Find our guild and enemies
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_data = stats
            elif alliance_name and alliance_name.lower() in guild.lower():
                # This is an alliance guild
                pass
            else:
                # This is an enemy guild
                enemies_data[guild] = stats
        
        if guild_data:
            # Update guild stats
            guild_stats['total_kills'] += guild_data['total_kills']
            guild_stats['total_deaths'] += guild_data['total_deaths']
            guild_stats['total_fame'] += guild_data['total_fame']
            guild_stats['battles'] += 1
            
            # Determine if battle was won
            guild_kd = guild_data['total_kills'] / max(1, guild_data['total_deaths'])
            enemy_kills = sum(stats['total_kills'] for stats in enemies_data.values())
            enemy_deaths = sum(stats['total_deaths'] for stats in enemies_data.values())
            enemy_kd = enemy_kills / max(1, enemy_deaths)
            
            if guild_kd > enemy_kd:
                guild_stats['wins'] += 1
            
            # Update enemy guild stats
            for guild, stats in enemies_data.items():
                if guild not in enemy_guilds:
                    enemy_guilds[guild] = {
                        'name': guild,  # Adicionar o nome da guild para o gráfico
                        'battles': 0,
                        'total_kills': 0,
                        'total_deaths': 0,
                        'total_fame': 0
                    }
                
                enemy_guilds[guild]['battles'] += 1
                enemy_guilds[guild]['total_kills'] += stats['total_kills']
                enemy_guilds[guild]['total_deaths'] += stats['total_deaths']
                enemy_guilds[guild]['total_fame'] += stats['total_fame']
    
    # Calculate KD ratios
    guild_stats['kd_ratio'] = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
    guild_stats['win_rate'] = (guild_stats['wins'] / max(1, guild_stats['battles'])) * 100
    
    for guild in enemy_guilds:
        enemy_guilds[guild]['kd_ratio'] = (
            enemy_guilds[guild]['total_kills'] / 
            max(1, enemy_guilds[guild]['total_deaths'])
        )
    
    # Filter enemy guilds with minimum battles
    min_battles = 2
    filtered_enemies = {
        guild: stats for guild, stats in enemy_guilds.items() 
        if stats['battles'] >= min_battles
    }
    
    if not filtered_enemies:
        st.warning(f"No enemy guilds found with at least {min_battles} battles against us.")
        return
    
    # Guild comparison section
    st.subheader("⚔️ Guild vs Enemy Comparison")
    
    # Comparison metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Our Total Battles", guild_stats['battles'])
        st.metric("Our Win Rate", f"{guild_stats['win_rate']:.1f}%")
    
    with col2:
        st.metric("Our K/D Ratio", f"{guild_stats['kd_ratio']:.2f}")
        st.metric("Our Total Kills", guild_stats['total_kills'])
    
    with col3:
        st.metric("Rival Guilds", len(filtered_enemies))
        st.metric("Our Total Deaths", guild_stats['total_deaths'])
    
    # Comparison charts
    st.subheader("📊 Guild Performance Comparison")
    
    # Metric selection
    metric = st.selectbox(
        "Compare by:",
        options=["kd_ratio", "kills", "deaths", "fame"],
        format_func=lambda x: {
            'kd_ratio': 'K/D Ratio',
            'kills': 'Kills',
            'deaths': 'Deaths',
            'fame': 'Fame'
        }[x]
    )
    
    # Create comparison chart
    fig = create_guild_comparison_chart(guild_stats, filtered_enemies, metric)
    st.plotly_chart(fig, use_container_width=True)
    
    # Enemy guilds detailed comparison
    st.subheader("🔍 Enemy Guilds Analysis")
    
    # Convert enemy data to DataFrame for display
    enemies_df = []
    for guild, stats in filtered_enemies.items():
        enemies_df.append({
            'Guild': guild,
            'Battles': stats['battles'],
            'Total Kills': stats['total_kills'],
            'Total Deaths': stats['total_deaths'],
            'K/D Ratio': stats['kd_ratio'],
            'Total Fame': stats['total_fame']
        })
    
    enemies_df = pd.DataFrame(enemies_df)
    enemies_df = enemies_df.sort_values('Battles', ascending=False)
    
    # Format the K/D Ratio column
    enemies_df['K/D Ratio'] = enemies_df['K/D Ratio'].round(2)
    
    # Display the table
    st.dataframe(
        enemies_df,
        use_container_width=True,
        height=300
    )
    
    # Battle analysis by enemy guild
    st.subheader("⚙️ Battle History Analysis")
    
    # Select enemy guild for detailed analysis
    if len(filtered_enemies) > 0:
        enemy_options = list(filtered_enemies.keys())
        selected_enemy = st.selectbox("Select Enemy Guild", options=enemy_options)
        
        if selected_enemy:
            # Find battles with this enemy
            enemy_battles = []
            
            for _, battle in battles_df.iterrows():
                details = battle['details']
                guild_found = False
                enemy_found = False
                
                for guild, _ in details['guilds'].items():
                    if guild_name.lower() in guild.lower():
                        guild_found = True
                    elif selected_enemy.lower() in guild.lower():
                        enemy_found = True
                
                if guild_found and enemy_found:
                    enemy_battles.append(battle)
            
            if enemy_battles:
                enemy_battles_df = pd.DataFrame(enemy_battles)
                
                # Display battle history
                st.write(f"### Battles against {selected_enemy}")
                
                # Calculate win/loss record
                wins = 0
                for _, battle in enemy_battles_df.iterrows():
                    details = battle['details']
                    guild_stats = None
                    enemy_stats = None
                    
                    for guild, stats in details['guilds'].items():
                        if guild_name.lower() in guild.lower():
                            guild_stats = stats
                        elif selected_enemy.lower() in guild.lower():
                            enemy_stats = stats
                    
                    if guild_stats and enemy_stats:
                        guild_kd = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
                        enemy_kd = enemy_stats['total_kills'] / max(1, enemy_stats['total_deaths'])
                        
                        if guild_kd > enemy_kd:
                            wins += 1
                
                losses = len(enemy_battles) - wins
                
                # Display win/loss record
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Battles", len(enemy_battles))
                
                with col2:
                    st.metric("Wins", wins)
                
                with col3:
                    st.metric("Losses", losses)
                
                # Create win/loss pie chart
                labels = ['Wins', 'Losses']
                values = [wins, losses]
                colors = ['#50fa7b', '#ff5555']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.3,
                    marker_colors=colors
                )])
                
                fig.update_layout(
                    title=f"Win/Loss Record against {selected_enemy}",
                    paper_bgcolor="#2d2d42",
                    font=dict(color="#f8f8f2")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display individual battles
                st.write("#### Battle History")
                
                for i, battle in enumerate(enemy_battles):
                    battle_time = battle['time'].strftime('%Y-%m-%d %H:%M')
                    
                    # Get guild and enemy stats from this battle
                    details = battle['details']
                    guild_stats = None
                    enemy_stats = None
                    
                    for guild, stats in details['guilds'].items():
                        if guild_name.lower() in guild.lower():
                            guild_stats = stats
                        elif selected_enemy.lower() in guild.lower():
                            enemy_stats = stats
                    
                    if guild_stats and enemy_stats:
                        guild_kd = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
                        enemy_kd = enemy_stats['total_kills'] / max(1, enemy_stats['total_deaths'])
                        
                        victory = guild_kd > enemy_kd
                        result_color = "#50fa7b" if victory else "#ff5555"
                        result_text = "VICTORY" if victory else "DEFEAT"
                        
                        st.markdown(f"""
                        <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0;">{battle_time}</h4>
                                <span style="color: {result_color}; font-weight: bold;">{result_text}</span>
                            </div>
                            <div style="display: flex; margin-top: 15px;">
                                <div style="flex: 1; text-align: center; border-right: 1px solid #6272a4; padding-right: 10px;">
                                    <h5>{guild_name}</h5>
                                    <p>Players: {len(guild_stats['players'])}</p>
                                    <p>Kills: {guild_stats['total_kills']}</p>
                                    <p>Deaths: {guild_stats['total_deaths']}</p>
                                    <p>K/D: {guild_kd:.2f}</p>
                                </div>
                                <div style="flex: 1; text-align: center; padding-left: 10px;">
                                    <h5>{selected_enemy}</h5>
                                    <p>Players: {len(enemy_stats['players'])}</p>
                                    <p>Kills: {enemy_stats['total_kills']}</p>
                                    <p>Deaths: {enemy_stats['total_deaths']}</p>
                                    <p>K/D: {enemy_kd:.2f}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
            else:
                st.warning(f"No direct battles found against {selected_enemy}.")
