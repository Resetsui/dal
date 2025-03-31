with st.sidebar:
    st.header("⚙️")
    st.subheader("Filtros de Batalha")

    # Min guild players filter
    min_guild_players = st.slider(
        "Mínimo de jogadores por batalha",
        min_value=1,
        max_value=50,
        value=1
    )

    # Days to look back
    days_back = st.slider(
        "Dias a considerar",
        min_value=1,
        max_value=30,
        value=7
    )

# Fetch data
start_date = datetime.now() - timedelta(days=days_back)
battles_data = scrape_battles(GUILD_ID, days_back)
guild_info = scrape_guild_info(GUILD_ID)
processed_data = process_battles_data(battles_data, GUILD_ID, GUILD_NAME, ALLIANCE_NAME)

# Filter battles by minimum guild players
battles_df = processed_data['battles']
filtered_battles = battles_df[battles_df['guild_players'] >= min_guild_players]

# Get guild statistics
guild_stats = get_guild_statistics(filtered_battles, processed_data['players'])

# Calculate metrics for overview
total_battles = len(filtered_battles)
active_players = guild_stats['active_players']
victories = len(filtered_battles[filtered_battles['battle_result'] == 'Victory'])
win_rate = victories / total_battles * 100 if total_battles > 0 else 0
total_kills = filtered_battles['guild_kills'].sum()
total_deaths = filtered_battles['guild_deaths'].sum()
overall_kd = total_kills / max(total_deaths, 1)

# Filter only guild players
guild_players_df = processed_data['players'][processed_data['players']['is_guild_member'] == True]
if len(guild_players_df) > 0:
    guild_players_df['kd_ratio'] = guild_players_df['kills'] / guild_players_df['deaths'].clip(lower=1)

# Find top performers
top_killer = guild_players_df.sort_values('kills', ascending=False).iloc[0] if len(guild_players_df) > 0 else None
top_kd_player = guild_players_df.sort_values('kd_ratio', ascending=False).iloc[0] if len(guild_players_df) > 0 else None
top_deaths_player = guild_players_df.sort_values('deaths', ascending=False).iloc[0] if len(guild_players_df) > 0 else None
most_active_player = guild_players_df.sort_values('battles', ascending=False).iloc[0] if len(guild_players_df) > 0 else None

# TAB 1: Overview
with tab1:
    # Main dashboard
    st.header("Visão Geral da Guild")

    # Stats in columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total de Batalhas", total_battles)

    with col2:
        st.metric("Jogadores Ativos", active_players)

    with col3:
        st.metric("Batalhas Vencidas", victories)

    with col4:
        st.metric("Taxa de Vitória", f"{win_rate:.1f}%")

    with col5:
        st.metric("K/D Geral", f"{overall_kd:.2f}")

    with col6:
        st.metric("Total de Kills", total_kills)

    # Top performers section
    st.header("🏆 Top Performers")

    # Calculate total silver cost for all deaths in the last 7 days
    total_silver_cost = total_deaths * 1777000  # 1.777M per death

    # Show total silver cost for 7 days
    st.markdown(f"""
    <div style="background-color: #3A3A3A; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;">
        <h3 style="color: #CFB53B; margin-top: 0;">💰 Custo Total nos Últimos {days_back} Dias</h3>
        <p style="font-size: 24px; margin: 5px 0;">{total_silver_cost/1000000:.3f}M Silver</p>
    </div>
    """, unsafe_allow_html=True)

    # Show top performers in columns
    performer_cols = st.columns(4)

    with performer_cols[0]:
        if top_killer is not None:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #FF5252; margin-top: 0;">🎯 Mestre das Kills</h3>
                <h2 style="margin: 5px 0; color: #FFD54F;">{top_killer['name']}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{top_killer['kills']}</p>
                    <p style="margin: 0; font-size: 14px;">Total Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{top_killer['kills'] / max(top_killer['deaths'], 1):.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FFD54F;">{top_killer['battles']}</p>
                    <p style="margin: 0; font-size: 14px;">Batalhas</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with performer_cols[1]:
        if top_kd_player is not None:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #64B5F6; margin-top: 0;">🏆 MVP</h3>
                <h2 style="margin: 5px 0; color: #FFD54F;">{top_kd_player['name']}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{top_kd_player['kd_ratio']:.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{top_kd_player['kills']}</p>
                    <p style="margin: 0; font-size: 14px;">Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{top_kd_player['deaths']}</p>
                    <p style="margin: 0; font-size: 14px;">Deaths</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with performer_cols[2]:
        if top_deaths_player is not None:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #9E9E9E; margin-top: 0;">💀 Campeão de Mortes</h3>
                <h2 style="margin: 5px 0; color: #FFD54F;">{top_deaths_player['name']}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{top_deaths_player['deaths']}</p>
                    <p style="margin: 0; font-size: 14px;">Total Mortes</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{top_deaths_player['kills']}</p>
                    <p style="margin: 0; font-size: 14px;">Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{top_deaths_player['kills'] / max(top_deaths_player['deaths'], 1):.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with performer_cols[3]:
        if most_active_player is not None:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #4CAF50; margin-top: 0;">⚔️ Mais Ativo</h3>
                <h2 style="margin: 5px 0; color: #FFD54F;">{most_active_player['name']}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FFD54F;">{most_active_player['battles']}</p>
                    <p style="margin: 0; font-size: 14px;">Batalhas</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{most_active_player['kills']}</p>
                    <p style="margin: 0; font-size: 14px;">Total Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{most_active_player['deaths']}</p>
                    <p style="margin: 0; font-size: 14px;">Total Mortes</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recent battles section
    st.header("⚔️ Batalhas Recentes")

    if len(filtered_battles) == 0:
        st.info("Não foram encontradas batalhas com os filtros atuais.")
    else:
        # Display recent battles
        sorted_battles = filtered_battles.sort_values('time', ascending=False)

        for idx, battle in sorted_battles.head(5).iterrows():
            battle_time = battle['time']
            battle_result = battle['battle_result']
            guild_kills = battle['guild_kills']
            guild_deaths = battle['guild_deaths']
            kd_ratio = battle['kd_ratio']
            total_players = battle['total_players']

            # Extract enemy guilds from battle records if available
            enemy_guilds = []
            for battle_data in battles_data:
                if str(battle_data.get('id', '')) == str(battle['id']):
                    # Extract unique guilds from battle data
                    guilds = set()
                    for player_data in battle_data.get('players', {}).values():
                        guild_name = player_data.get('guildName', '')
                        if guild_name and guild_name != GUILD_NAME:
                            guilds.add(guild_name)
                    enemy_guilds = list(guilds)
                    break

            enemy_guilds_str = " | ".join(enemy_guilds[:5])  # Limit to 5 enemies for display
            if len(enemy_guilds) > 5:
                enemy_guilds_str += " | ..."

            result_color = "#4CAF50" if battle_result == "Victory" else "#F44336"

            # Create expandable battle card
            with st.expander(f"⚔️ {battle_time.strftime('%d/%m/%Y %H:%M')} vs {enemy_guilds_str}", expanded=False):
                st.markdown(f"K/D: {kd_ratio:.2f}")
                st.markdown(f"{battle_time.strftime('%d/%m/%Y %H:%M')}")

                st.markdown(f"""
                <div style="background-color: {result_color}; padding: 5px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin: 5px 0;">
                    {battle_result.upper()}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"Kills: {guild_kills} | Deaths: {guild_deaths} | K/D: {kd_ratio:.2f}")
                st.markdown(f"Jogadores: {total_players}")

                # Battle details button
                if st.button(f"Ver Detalhes da Batalha {battle['id']}", key=f"battle_details_{battle['id']}"):
                    battle_details = scrape_battle_details(battle['id'])

                    if battle_details:
                        st.subheader("Detalhes da Batalha")
                        st.markdown(f"**Data**: {battle_time.strftime('%d/%m/%Y %H:%M')}")

                        # Battle result as only K/D ratio, not the redundant victory/defeat text
                        st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: bold;">
                            K/D: {kd_ratio:.2f}
                        </div>
                        """, unsafe_allow_html=True)

                        # Create columns for guild stats
                        guild_stats_cols = st.columns(3)

                        # Calculate Alliance stats (excluding We Profit)
                        alliance_guilds = []
                        alliance_players = 0
                        alliance_kills = 0
                        alliance_deaths = 0

                        # Calculate enemy guild stats
                        enemy_guilds = []
                        enemy_players = 0
                        enemy_kills = 0
                        enemy_deaths = 0

                        # Get guild lists
                        alliance_guild_names = []
                        enemy_guild_names = []

                        for guild_name, stats in battle_details['guilds'].items():
                            if guild_name == GUILD_NAME:
                                continue

                            is_ally = False
                            for player_name, player_stats in battle_details['players'].items():
                                if player_stats['guild'] == guild_name and 'alliance' in player_stats and player_stats['alliance'] == ALLIANCE_NAME:
                                    is_ally = True
                                    break

                            if is_ally:
                                alliance_guilds.append(guild_name)
                                alliance_guild_names.append(guild_name)
                                alliance_players += stats['players']
                                alliance_kills += stats['kills']
                                alliance_deaths += stats['deaths']
                            else:
                                enemy_guilds.append(guild_name)
                                enemy_guild_names.append(guild_name)
                                enemy_players += stats['players']
                                enemy_kills += stats['kills']
                                enemy_deaths += stats['deaths']

                        # Format guild names for display
                        alliance_guild_names_str = ", ".join(alliance_guild_names) if alliance_guild_names else "None"
                        enemy_guild_names_str = ", ".join(enemy_guild_names) if enemy_guild_names else "None"

                        # Our guild stats
                        with guild_stats_cols[0]:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px;">
                                <h3 style="color: #FFD54F; margin-top: 0; text-align: center;">We Profit</h3>
                                <div style="display: flex; flex-direction: column;">
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Players</span>
                                        <span style="font-size: 18px; font-weight: bold;">{battle['guild_players']}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>K/D</span>
                                        <span style="font-size: 18px; font-weight: bold;">{kd_ratio:.2f}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Kills</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FF5252;">{guild_kills}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Deaths</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #9E9E9E;">{guild_deaths}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Fame</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FFD54F;">{battle['total_fame']:,.0f}</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Alliance stats
                        with guild_stats_cols[1]:
                            alliance_kd = alliance_kills / max(alliance_deaths, 1)
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px;">
                                <h3 style="color: #64B5F6; margin-top: 0; text-align: center;">Alliance</h3>
                                <p style="font-size: 12px; color: #aaa; margin-bottom: 12px; text-align: center;">{alliance_guild_names_str}</p>
                                <div style="display: flex; flex-direction: column;">
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Players</span>
                                        <span style="font-size: 18px; font-weight: bold;">{alliance_players}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>K/D</span>
                                        <span style="font-size: 18px; font-weight: bold;">{alliance_kd:.2f}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Kills</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FF5252;">{alliance_kills}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Deaths</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #9E9E9E;">{alliance_deaths}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Fame</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FFD54F;">0</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Enemy stats
                        with guild_stats_cols[2]:
                            enemy_kd = enemy_kills / max(enemy_deaths, 1)
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px;">
                                <h3 style="color: #FF5252; margin-top: 0; text-align: center;">Enemies</h3>
                                <p style="font-size: 12px; color: #aaa; margin-bottom: 12px; text-align: center;">{enemy_guild_names_str}</p>
                                <div style="display: flex; flex-direction: column;">
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Players</span>
                                        <span style="font-size: 18px; font-weight: bold;">{enemy_players}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>K/D</span>
                                        <span style="font-size: 18px; font-weight: bold;">{enemy_kd:.2f}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Kills</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FF5252;">{enemy_kills}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Deaths</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #9E9E9E;">{enemy_deaths}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                                        <span>Fame</span>
                                        <span style="font-size: 18px; font-weight: bold; color: #FFD54F;">0</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Calculate total silver cost
                        total_deaths = guild_deaths + alliance_deaths + enemy_deaths
                        silver_cost = total_deaths * 1777000  # 1.777M per death

                        # Display silver cost
                        st.markdown(f"""
                        <div style="background-color: #3A3A3A; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;">
                            <h3 style="color: #CFB53B; margin-top: 0;">💰 Custo Total DA BATALHA</h3>
                            <p style="font-size: 20px; margin: 5px 0;">{silver_cost/1000000:.3f}M Silver</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Player Performance section
                        st.markdown("## 🎮 Player Performance")

                        # Convert players dict to dataframe for easier sorting
                        players_list = []
                        for player_name, stats in battle_details['players'].items():
                            if stats['guild'] == GUILD_NAME:  # Only include We Profit players
                                players_list.append({
                                    'name': player_name,
                                    'guild': stats['guild'],
                                    'kills': stats['kills'],
                                    'deaths': stats['deaths'],
                                    'kd': stats['kills'] / max(stats['deaths'], 1)
                                })

                        players_df = pd.DataFrame(players_list)

                        # Top Killers and Most Deaths sections
                        top_killer_cols = st.columns(2)

                        with top_killer_cols[0]:
                            st.markdown("### 🎯 Top Killers")

                            if len(players_df) > 0:
                                # Sort by kills
                                top_killers = players_df.sort_values('kills', ascending=False).head(3)

                                # Medals
                                medals = ["🥇", "🥈", "🥉"]

                                for i, (_, player) in enumerate(top_killers.iterrows()):
                                    if i < len(medals):
                                        medal = medals[i]
                                    else:
                                        medal = "🏅"

                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                                        <h4 style="margin: 0;">{medal} {player['name']}</h4>
                                        <p style="margin: 5px 0;">Kills: {player['kills']}</p>
                                        <p style="margin: 5px 0;">Deaths: {player['deaths']}</p>
                                        <p style="margin: 5px 0;">K/D: {player['kd']:.2f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("Não há dados de jogadores disponíveis.")

                        with top_killer_cols[1]:
                            st.markdown("### 💀 Most Deaths")

                            if len(players_df) > 0:
                                # Sort by deaths
                                most_deaths = players_df.sort_values('deaths', ascending=False).head(3)

                                # Death icons
                                death_icons = ["💀", "☠️", "👻"]

                                for i, (_, player) in enumerate(most_deaths.iterrows()):
                                    if i < len(death_icons):
                                        icon = death_icons[i]
                                    else:
                                        icon = "💀"

                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                                        <h4 style="margin: 0;">{icon} {player['name']}</h4>
                                        <p style="margin: 5px 0;">Deaths: {player['deaths']}</p>
                                        <p style="margin: 5px 0;">Kills: {player['kills']}</p>
                                        <p style="margin: 5px 0;">K/D: {player['kd']:.2f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("Não há dados de jogadores disponíveis.")

                        # Player Statistics table
                        st.markdown("## 📊 Player Statistics")

                        if len(players_df) > 0:
                            # Add K/D ratio and format the table
                            players_df['kd'] = players_df['kd'].round(2)
                            players_df = players_df.sort_values('kills', ascending=False)

                            # Create a simplified table view
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="border-bottom: 1px solid #444;">
                                            <th style="padding: 8px; text-align: left;">Nome</th>
                                            <th style="padding: 8px; text-align: center;">Kills</th>
                                            <th style="padding: 8px; text-align: center;">Deaths</th>
                                            <th style="padding: 8px; text-align: center;">K/D</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                            """, unsafe_allow_html=True)

                            # Add rows for each player (limit to top 10)
                            for i, (_, player) in enumerate(players_df.head(10).iterrows()):
                                kd_color = "#4CAF50" if player['kd'] >= 1 else "#F44336"
                                st.markdown(f"""
                                    <tr style="border-bottom: 1px solid #333;">
                                        <td style="padding: 6px; text-align: left; font-weight: bold;">{player['name']}</td>
                                        <td style="padding: 6px; text-align: center; color: #FF5252;">{player['kills']}</td>
                                        <td style="padding: 6px; text-align: center; color: #9E9E9E;">{player['deaths']}</td>
                                        <td style="padding: 6px; text-align: center; color: {kd_color};">{player['kd']:.2f}</td>
                                    </tr>
                                """, unsafe_allow_html=True)

                            st.markdown("""
                                    </tbody>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Não há dados de jogadores disponíveis.")

                        # Participating Guilds
                        st.markdown("## ⚔️ Participating Guilds")

                        # Allies section
                        st.markdown("### 🛡️ Aliados na Batalha")

                        ally_cols = st.columns(min(3, len(alliance_guilds) + 1))

                        # Our guild
                        with ally_cols[0]:
                            our_stats = battle_details['guilds'].get(GUILD_NAME, {})
                            our_kd = our_stats.get('kills', 0) / max(our_stats.get('deaths', 0), 1)

                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                                <h4 style="color: #FFD54F; margin: 0;">{GUILD_NAME}</h4>
                                <p style="margin: 5px 0;">👥 Players: {our_stats.get('players', 0)}</p>
                                <p style="margin: 5px 0;">⚔️ Kills: {our_stats.get('kills', 0)}</p>
                                <p style="margin: 5px 0;">💀 Deaths: {our_stats.get('deaths', 0)}</p>
                                <p style="margin: 5px 0;">K/D: {our_kd:.2f}</p>
                                <p style="margin: 5px 0;">🏆 Fame: {our_stats.get('fame', 0)}</p>
```</div>
                            """, unsafe_allow_html=True)

                        # Alliance guilds
                        for i, guild_name in enumerate(alliance_guilds):
                            with ally_cols[(i + 1) % len(ally_cols)]:
                                stats = battle_details['guilds'].get(guild_name, {})
                                guild_kd = stats.get('kills', 0) / max(stats.get('deaths', 0), 1)

                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                                    <h4 style="color: #64B5F6; margin: 0;">{guild_name}</h4>
                                    <p style="margin: 5px 0;">👥 Players: {stats.get('players', 0)}</p>
                                    <p style="margin: 5px 0;">⚔️ Kills: {stats.get('kills', 0)}</p>
                                    <p style="margin: 5px 0;">💀 Deaths: {stats.get('deaths', 0)}</p>
                                    <p style="margin: 5px 0;">K/D: {guild_kd:.2f}</p>
                                    <p style="margin: 5px 0;">🏆 Fame: {stats.get('fame', 0)}</p>
                                </div>
                                """, unsafe_allow_html=True)

                        # Enemy guilds section
                        st.markdown("### 🔍 Detalhes dos Oponentes")

                        enemy_cols = st.columns(min(3, len(enemy_guilds)))

                        for i, guild_name in enumerate(enemy_guilds):
                            with enemy_cols[i % len(enemy_cols)]:
                                stats = battle_details['guilds'].get(guild_name, {})
                                guild_kd = stats.get('kills', 0) / max(stats.get('deaths', 0), 1)

                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                                    <h4 style="color: #FF5252; margin: 0;">{guild_name}</h4>
                                    <p style="margin: 5px 0;">👥 Players: {stats.get('players', 0)}</p>
                                    <p style="margin: 5px 0;">⚔️ Kills: {stats.get('kills', 0)}</p>
                                    <p style="margin: 5px 0;">💀 Deaths: {stats.get('deaths', 0)}</p>
                                    <p style="margin: 5px 0;">K/D: {guild_kd:.2f}</p>
                                    <p style="margin: 5px 0;">🏆 Fame: {stats.get('fame', 0)}</p>
                                </div>
                                """, unsafe_allow_html=True)

                        # Comparative chart
                        st.markdown("## 📊 Comparativo de Guilds")

                        # Prepare data for chart
                        guilds_data = []

                        # Our guild
                        our_stats = battle_details['guilds'].get(GUILD_NAME, {})
                        guilds_data.append({
                            'Guild': GUILD_NAME,
                            'Players': our_stats.get('players', 0),
                            'Kills': our_stats.get('kills', 0),
                            'Deaths': our_stats.get('deaths', 0),
                            'K/D': our_stats.get('kills', 0) / max(our_stats.get('deaths', 0), 1),
                            'Type': 'Our Guild'
                        })

                        # Alliance guilds
                        for guild_name in alliance_guilds:
                            stats = battle_details['guilds'].get(guild_name, {})
                            guilds_data.append({
                                'Guild': guild_name,
                                'Players': stats.get('players', 0),
                                'Kills': stats.get('kills', 0),
                                'Deaths': stats.get('deaths', 0),
                                'K/D': stats.get('kills', 0) / max(stats.get('deaths', 0), 1),
                                'Type': 'Alliance'
                            })

                        # Enemy guilds
                        for guild_name in enemy_guilds:
                            stats = battle_details['guilds'].get(guild_name, {})
                            guilds_data.append({
                                'Guild': guild_name,
                                'Players': stats.get('players', 0),
                                'Kills': stats.get('kills', 0),
                                'Deaths': stats.get('deaths', 0),
                                'K/D': stats.get('kills', 0) / max(stats.get('deaths', 0), 1),
                                'Type': 'Enemy'
                            })

                        # Create dataframe
                        guilds_df = pd.DataFrame(guilds_data)

                        # Create K/D comparison chart
                        fig = px.bar(
                            guilds_df,
                            x='Guild',
                            y='K/D',
                            color='Type',
                            color_discrete_map={
                                'Our Guild': '#FFD54F',
                                'Alliance': '#64B5F6',
                                'Enemy': '#FF5252'
                            },
                            title='Guild K/D Ratio Comparison'
                        )

                        fig.update_layout(template='plotly_dark')
                        st.plotly_chart(fig, use_container_width=True)

                        # Create Players comparison chart
                        fig = px.bar(
                            guilds_df,
                            x='Guild',
                            y='Players',
                            color='Type',
                            color_discrete_map={
                                'Our Guild': '#FFD54F',
                                'Alliance': '#64B5F6',
                                'Enemy': '#FF5252'
                            },
                            title='Guild Player Count Comparison'
                        )

                        fig.update_layout(template='plotly_dark')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Não foi possível obter detalhes desta batalha.")

# TAB 2: Player Rankings
with tab2:
    st.header("👑 Player Rankings")
    st.subheader("Ranking de Jogadores")
    st.markdown("Análise detalhada da performance individual dos membros de We Profit")

    # Use all players with at least 1 battle
    min_battles_for_ranking = 1
    ranked_players = guild_players_df[guild_players_df['battles'] >= min_battles_for_ranking]

    # Create tabs for different rankings
    ranking_tabs = st.tabs(["Kills", "K/D Ratio", "Deaths", "Participação"])

    # Tab for kills ranking
    with ranking_tabs[0]:
        st.subheader("Ranking por Kills")
        kills_players = ranked_players.sort_values('kills', ascending=False).head(10)

        # Display as cards in grid
        kills_cols = st.columns(3)
        for i, (_, player) in enumerate(kills_players.iterrows()):
            with kills_cols[i % 3]:
                kd_color = "#4CAF50" if player['kd_ratio'] >= 1 else "#F44336"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 5px 0; color: #FFD54F; text-align: center;">{player['name']}</h3>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Kills</span>
                        <span style="font-weight: bold; color: #FF5252;">{player['kills']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Deaths</span>
                        <span style="font-weight: bold; color: #9E9E9E;">{player['deaths']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>K/D</span>
                        <span style="font-weight: bold; color: {kd_color};">{player['kd_ratio']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Batalhas</span>
                        <span style="font-weight: bold;">{player['battles']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Tab for KD ratio ranking
    with ranking_tabs[1]:
        st.subheader("Ranking por K/D Ratio")
        kd_players = ranked_players.sort_values('kd_ratio', ascending=False).head(10)

        # Display as cards in grid
        kd_cols = st.columns(3)
        for i, (_, player) in enumerate(kd_players.iterrows()):
            with kd_cols[i % 3]:
                kd_color = "#4CAF50" if player['kd_ratio'] >= 1 else "#F44336"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 5px 0; color: #FFD54F; text-align: center;">{player['name']}</h3>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>K/D</span>
                        <span style="font-weight: bold; color: {kd_color};">{player['kd_ratio']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Kills</span>
                        <span style="font-weight: bold; color: #FF5252;">{player['kills']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Deaths</span>
                        <span style="font-weight: bold; color: #9E9E9E;">{player['deaths']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Batalhas</span>
                        <span style="font-weight: bold;">{player['battles']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Tab for Deaths ranking
    with ranking_tabs[2]:
        st.subheader("Ranking por Deaths")
        deaths_players = ranked_players.sort_values('deaths', ascending=False).head(10)

        # Display as cards in grid
        deaths_cols = st.columns(3)
        for i, (_, player) in enumerate(deaths_players.iterrows()):
            with deaths_cols[i % 3]:
                kd_color = "#4CAF50" if player['kd_ratio'] >= 1 else "#F44336"
                # Calculate silver cost
                silver_cost = player['deaths'] * 1777000

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 5px 0; color: #FFD54F; text-align: center;">{player['name']}</h3>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Deaths</span>
                        <span style="font-weight: bold; color: #9E9E9E;">{player['deaths']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Custo</span>
                        <span style="font-weight: bold; color: #CFB53B;">{silver_cost/1000000:.3f}M</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Kills</span>
                        <span style="font-weight: bold; color: #FF5252;">{player['kills']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>K/D</span>
                        <span style="font-weight: bold; color: {kd_color};">{player['kd_ratio']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Tab for Battle Participation
    with ranking_tabs[3]:
        st.subheader("Ranking por Participação em Batalhas")
        battles_players = ranked_players.sort_values('battles', ascending=False).head(10)

        # Display as cards in grid
        battles_cols = st.columns(3)
        for i, (_, player) in enumerate(battles_players.iterrows()):
            with battles_cols[i % 3]:
                kd_color = "#4CAF50" if player['kd_ratio'] >= 1 else "#F44336"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 5px 0; color: #FFD54F; text-align: center;">{player['name']}</h3>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Batalhas</span>
                        <span style="font-weight: bold;">{player['battles']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Kills</span>
                        <span style="font-weight: bold; color: #FF5252;">{player['kills']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>Deaths</span>
                        <span style="font-weight: bold; color: #9E9E9E;">{player['deaths']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                        <span>K/D</span>
                        <span style="font-weight: bold; color: {kd_color};">{player['kd_ratio']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Detailed player statistics section
    st.header("Detailed Player Statistics")

    # Display top performers again in cards
    st.subheader("🏆 Top Performers")

    # Create 4 columns for top performers
    top_cols = st.columns(4)

    # Top Killer
    with top_cols[0]:
        if top_killer is not None:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #FF5252; margin-top: 0;">🎯 Kill Master</h3>
                <h2 style="margin: 5px 0;">{}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Total Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{:.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FFD54F;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Battles</p>
                </div>
            </div>
            """.format(top_killer['name'], top_killer['kills'], 
                      top_killer['kills'] / max(top_killer['deaths'], 1), 
                      top_killer['battles']), unsafe_allow_html=True)

    # Top Deaths
    with top_cols[1]:
        if top_deaths_player is not None:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #9E9E9E; margin-top: 0;">💀 Death Champion</h3>
                <h2 style="margin: 5px 0;">{}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Total Deaths</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{:.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
            </div>
            """.format(top_deaths_player['name'], top_deaths_player['deaths'], 
                      top_deaths_player['kills'], 
                      top_deaths_player['kills'] / max(top_deaths_player['deaths'], 1)), 
                      unsafe_allow_html=True)

    # MVP (Highest K/D)
    with top_cols[2]:
        if top_kd_player is not None:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #FFD54F; margin-top: 0;">🏆 MVP</h3>
                <h2 style="margin: 5px 0;">{}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #64B5F6;">{:.2f}</p>
                    <p style="margin: 0; font-size: 14px;">K/D Ratio</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Deaths</p>
                </div>
            </div>
            """.format(top_kd_player['name'], top_kd_player['kd_ratio'], 
                      top_kd_player['kills'], top_kd_player['deaths']), 
                      unsafe_allow_html=True)

    # Most Active
    with top_cols[3]:
        if most_active_player is not None:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e2531, #2c3040); padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: #A5D6A7; margin-top: 0;">⚔️ Most Active</h3>
                <h2 style="margin: 5px 0;">{}</h2>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #A5D6A7;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Battles</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #FF5252;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Total Kills</p>
                </div>
                <div style="margin: 20px 0;">
                    <p style="font-size: 24px; margin: 0; color: #9E9E9E;">{}</p>
                    <p style="margin: 0; font-size: 14px;">Total Deaths</p>
                </div>
            </div>
            """.format(most_active_player['name'], most_active_player['battles'], 
                      most_active_player['kills'], most_active_player['deaths']), 
                      unsafe_allow_html=True)

    # Efficiency analysis section
    st.header("📊 Análise de Eficiência dos Jogadores")
    st.subheader("🎯 Sistema de Pontuação de Eficiência")

    # Create efficiency scores for each player
    if len(ranked_players) > 0:
        ranked_players_list = []
        for _, player in ranked_players.iterrows():
            # Calculate efficiency score
            # Formula: (kills * 3 - deaths) / battles
            efficiency_score = ((player['kills'] * 3) - player['deaths']) / max(player['battles'], 1)

            ranked_players_list.append({
                'name': player['name'],
                'kills': player['kills'],
                'deaths': player['deaths'],
                'battles': player['battles'],
                'kd_ratio': player['kd_ratio'],
                'efficiency_score': efficiency_score,
                'silver_cost': player['deaths'] * 1777000  # 1.777M per death
            })

        efficiency_df = pd.DataFrame(ranked_players_list)
        efficiency_df = efficiency_df.sort_values('efficiency_score', ascending=False)

        # Show efficiency table
        st.dataframe(
            efficiency_df[['name', 'efficiency_score', 'kills', 'deaths', 'battles', 'kd_ratio', 'silver_cost']].rename(
                columns={
                    'name': 'Jogador',
                    'efficiency_score': 'Pontuação de Eficiência',
                    'kills': 'Kills',
                    'deaths': 'Mortes',
                    'battles': 'Batalhas',
                    'kd_ratio': 'K/D Ratio',
                    'silver_cost': 'Custo em Prata'
                }
            ).style.format({
                'Pontuação de Eficiência': '{:.2f}',
                'K/D Ratio': '{:.2f}',
                'Custo em Prata': '{:,.0f}'
            }),
            use_container_width=True
        )

        # Visualization of efficiency
        st.subheader("Visualização de Eficiência dos Jogadores")

        # Prepare data for chart - top 15 players by efficiency
        top_efficient = efficiency_df.head(15)

        # Create bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=top_efficient['name'],
            x=top_efficient['efficiency_score'],
            orientation='h',
            marker_color='rgba(75, 192, 192, 0.7)',
            name='Pontuação',
            text=top_efficient['efficiency_score'].round(2),
            textposition='auto',
        ))

        fig.update_layout(
            title='Top 15 Jogadores por Eficiência',
            xaxis_title='Pontuação de Eficiência',
            yaxis_title='',
            template='plotly_dark',
            height=600,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados suficientes para calcular a eficiência dos jogadores.")

# TAB 3: Attendance Info
with tab3:
    st.header("Informações de Atendimento")

    # Get the two week period for attendance check
    two_weeks_ago = datetime.now() - timedelta(days=14)

    # Count battles in the last two weeks
    # Convert both sides to the same timezone format for comparison
    filtered_battles_copy = filtered_battles.copy()
    filtered_battles_copy['time_for_compare'] = filtered_battles_copy['time'].dt.tz_localize(None)
    recent_battles = filtered_battles_copy[filtered_battles_copy['time_for_compare'] >= two_weeks_ago]
    total_recent_battles = len(recent_battles)

    st.subheader(f"Análise de Atendimento (Últimas 2 Semanas - {total_recent_battles} batalhas)")

    # Calculate attendance for each player
    if len(guild_players_df) > 0 and total_recent_battles > 0:
        attendance_list = []

        for _, player in guild_players_df.iterrows():
            # Estimate attendance based on battle count
            # Since we don't have explicit battle_ids, we'll use the player's total battles
            # and estimate what portion were in the last two weeks based on the ratio
            total_player_battles = player['battles']
            recent_ratio = len(recent_battles) / max(len(filtered_battles), 1)

            # Estimate battles in recent period (with upper limit of total recent battles)
            player_battles_in_period = min(int(total_player_battles * recent_ratio), total_recent_battles)

            # Calculate attendance percentage
            attendance_percentage = (player_battles_in_period / total_recent_battles) * 100

            attendance_list.append({
                'name': player['name'],
                'battles_attended': player_battles_in_period,
                'total_battles': total_recent_battles,
                'attendance_percentage': attendance_percentage
            })

        attendance_df = pd.DataFrame(attendance_list)

        # Sort by attendance percentage (high to low)
        high_attendance = attendance_df.sort_values('attendance_percentage', ascending=False)

        # Display high attendance players
        st.subheader("🏆 Jogadores com Maior Atendimento")

        # Create bar chart for high attendance
        fig_high = go.Figure()

        fig_high.add_trace(go.Bar(
            y=high_attendance.head(15)['name'],
            x=high_attendance.head(15)['attendance_percentage'],
            orientation='h',
            marker_color='rgba(75, 192, 192, 0.7)',
            name='Atendimento (%)',
            text=high_attendance.head(15)['attendance_percentage'].round(1).astype(str) + '%',
            textposition='auto',
        ))

        fig_high.update_layout(
            title='Top 15 Jogadores por Atendimento',
            xaxis_title='Porcentagem de Atendimento',
            yaxis_title='',
            template='plotly_dark',
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            xaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig_high, use_container_width=True)

        # Display low attendance players (less than 7 battles in 2 weeks)
        st.subheader("⚠️ Jogadores com Menos de 7 Atendimentos nas Últimas 2 Semanas")

        low_attendance = attendance_df[attendance_df['battles_attended'] < 7].sort_values('battles_attended')

        if len(low_attendance) > 0:
            # Create formatted table for low attendance
            st.markdown("""
            <style>
            .low-attendance-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .low-attendance-table th, .low-attendance-table td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #444;
            }
            .low-attendance-table th {
                background-color: #2c3040;
                color: #FFD54F;
                font-weight: bold;
            }
            .low-attendance-table tr:nth-child(even) {
                background-color: #23293a;
            }
            .low-attendance-table tr:hover {
                background-color: #333c4d;
            }
            .warning-cell {
                color: #FF5252;
                font-weight: bold;
            }
            </style>

            <table class="low-attendance-table">
                <tr>
                    <th>Jogador</th>
                    <th>Atendimentos</th>
                    <th>Total Batalhas</th>
                    <th>Porcentagem</th>
                </tr>
            """, unsafe_allow_html=True)

            for _, player in low_attendance.iterrows():
                st.markdown(f"""
                <tr>
                    <td>{player['name']}</td>
                    <td class="warning-cell">{player['battles_attended']}</td>
                    <td>{player['total_battles']}</td>
                    <td>{player['attendance_percentage']:.1f}%</td>
                </tr>
                """, unsafe_allow_html=True)

            st.markdown("</table>", unsafe_allow_html=True)
        else:
            st.success("Todos os jogadores possuem bom atendimento (7+ batalhas nas últimas 2 semanas).")
    else:
        st.warning("Não há dados suficientes para analisar o atendimento dos jogadores nas últimas 2 semanas.")
