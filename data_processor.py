import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from battle_history_manager import get_daily_stats as history_get_daily_stats

def get_battles_with_min_members(battles_df, guild_name, min_members=20, days=7):
    """
    Filter battles to include only those with minimum number of guild members
    and within the specified number of days
    """
    if battles_df.empty:
        return pd.DataFrame()

    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_battles = battles_df[battles_df['time'] >= cutoff_date].copy()

    if recent_battles.empty:
        return pd.DataFrame()

    # Filter by guild member count
    filtered_battles = []

    for _, battle in recent_battles.iterrows():
        details = battle['details']
        guild_found = False

        # Check each guild in the battle
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_found = True
                # Check if the guild has enough members
                if len(stats['players']) >= min_members:
                    filtered_battles.append(battle)
                break

    return pd.DataFrame(filtered_battles)

def get_guild_stats(battles_df, guild_name, alliance_name=None):
    """Calculate overall statistics for a guild from battle data"""
    if battles_df.empty:
        return {}

    total_battles = len(battles_df)
    total_kills = 0
    total_deaths = 0
    total_fame = 0
    battles_won = 0
    players_data = {}

    for _, battle in battles_df.iterrows():
        details = battle['details']
        guild_stats = None
        enemies_stats = {}

        # Find the specified guild and alliance members
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_stats = stats
                # Process player data
                for player in stats['players']:
                    name = player['name']
                    if name not in players_data:
                        players_data[name] = {
                            'kills': 0,
                            'deaths': 0,
                            'fame': 0,
                            'battles': 0
                        }

                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1
            elif alliance_name and alliance_name.lower() in guild.lower():
                # This is an alliance guild
                pass
            else:
                # This is an enemy guild
                enemies_stats[guild] = stats

        if guild_stats:
            total_kills += guild_stats['total_kills']
            total_deaths += guild_stats['total_deaths']
            total_fame += guild_stats['total_fame']

            # Determine if battle was won (kills > 60% more than deaths)
            guild_kills = guild_stats['total_kills']
            guild_deaths = max(1, guild_stats['total_deaths'])
            victory_threshold = guild_deaths * 1.6  # 60% more kills than deaths

            if guild_kills >= victory_threshold:
                battles_won += 1

    # Calculate win rate
    win_rate = (battles_won / total_battles) * 100 if total_battles > 0 else 0

    # Create stats dictionary
    guild_stats = {
        'total_battles': total_battles,
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'total_fame': total_fame,
        'battles_won': battles_won,
        'win_rate': win_rate,
        'kd_ratio': total_kills / max(1, total_deaths),
        'name': guild_name,
        'alliance': alliance_name,
        'players': players_data
    }

    return guild_stats

def get_recent_battles(battles_df, days=7):
    """Get battles from the last X days and sort them by time"""
    if battles_df.empty:
        return pd.DataFrame()

    cutoff_date = datetime.now() - timedelta(days=days)
    recent_battles = battles_df[battles_df['time'] >= cutoff_date]

    return recent_battles.sort_values('time', ascending=False).reset_index(drop=True)

def get_battle_details(battles_df, battle_id):
    """Extract details for a specific battle"""
    if battles_df.empty:
        return None

    battle = battles_df[battles_df['battle_id'] == battle_id]

    if battle.empty:
        return None

    return battle.iloc[0]

def get_top_players(battles_df, guild_name, metric='kills', limit=3):
    """Get top players by a specific metric (kills, deaths, fame)"""
    if battles_df.empty:
        return []

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
                            'battles': 0
                        }

                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1

    # Convert to DataFrame
    players_df = pd.DataFrame.from_dict(players_data, orient='index')

    # Calculate K/D ratio
    if not players_df.empty:
        players_df['kd_ratio'] = players_df['kills'] / players_df['deaths'].replace(0, 1)

    # Sort by the specified metric
    if players_df.empty or metric not in players_df.columns:
        return []

    return players_df.sort_values(metric, ascending=False).head(limit).to_dict('records')

def get_daily_stats(battles_df, guild_name, days=7):
    """Get daily statistics for kills and deaths using historic data"""
    if battles_df.empty:
        return pd.DataFrame()

    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Converter datas para UTC se necessário
    recent_battles = battles_df[battles_df['time'].dt.tz_convert('UTC') >= cutoff_date]

    if recent_battles.empty:
        return pd.DataFrame()

    # Criar coluna de data (apenas o dia)
    recent_battles = recent_battles.copy()
    recent_battles['date'] = recent_battles['time'].dt.date

    # Agrupar por dia
    daily_stats = recent_battles.groupby('date').agg({
        'battle_id': 'count',
        'kills': 'sum',
        'deaths': 'sum'
    }).reset_index()

    # Renomear a coluna battle_id para battles
    daily_stats.rename(columns={'battle_id': 'battles'}, inplace=True)

    # Calcular K/D ratio
    daily_stats['kd_ratio'] = daily_stats['kills'] / daily_stats['deaths'].replace(0, 1)

    # Calcular vitórias (assumindo que kills são 60% maiores que deaths é vitória)
    daily_stats['wins'] = 0
    for idx, row in daily_stats.iterrows():
        date = row['date']
        day_battles = recent_battles[recent_battles['date'] == date]
        daily_stats.at[idx, 'wins'] = sum(day_battles['kills'] >= (day_battles['deaths'] * 1.6))


    # Calcular taxa de vitórias
    daily_stats['win_rate'] = (daily_stats['wins'] / daily_stats['battles']) * 100

    # Ordenar por data
    daily_stats = daily_stats.sort_values('date')

    return daily_stats

def get_enemy_guilds(battles_df, guild_name, alliance_name=None):
    """Get list of enemy guilds and their stats"""
    if battles_df.empty:
        return {}

    enemy_guilds = {}

    for _, battle in battles_df.iterrows():
        details = battle['details']

        for guild, stats in details['guilds'].items():
            # Skip our guild and alliance
            if guild_name.lower() in guild.lower():
                continue
            if alliance_name and alliance_name.lower() in guild.lower():
                continue

            if guild not in enemy_guilds:
                enemy_guilds[guild] = {
                    'name': guild,
                    'kills': 0,
                    'deaths': 0,
                    'fame': 0,
                    'battles': 0,
                    'kd_ratio': 0
                }

            enemy_guilds[guild]['kills'] += stats['total_kills']
            enemy_guilds[guild]['deaths'] += stats['total_deaths']
            enemy_guilds[guild]['fame'] += stats['total_fame']
            enemy_guilds[guild]['battles'] += 1

    # Calculate K/D ratio for each enemy guild
    for guild in enemy_guilds:
        enemy_guilds[guild]['kd_ratio'] = enemy_guilds[guild]['kills'] / max(1, enemy_guilds[guild]['deaths'])

    return enemy_guilds