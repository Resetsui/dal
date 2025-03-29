import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

def generate_player_stats(name, min_kills=0, max_kills=15, min_deaths=0, max_deaths=10):
    """Generate random stats for a player"""
    kills = random.randint(min_kills, max_kills)
    deaths = random.randint(min_deaths, max_deaths)
    fame = kills * random.randint(5000, 15000)
    
    return {
        'name': name,
        'kills': kills,
        'deaths': deaths,
        'fame': fame
    }

def generate_mock_battle_data(guild_name="We Profit", alliance_name="Baiah", days=30):
    """
    Generate mock battle data for testing when the real API is not available
    """
    # Lista de membros da guild para gerar estatísticas
    guild_members = [
        "AngrySwordsman", "MagicHealer", "CrazyArcher", "TankMaster", 
        "ShadowAssassin", "FireMage", "IceWizard", "BerserkWarrior",
        "NinjaStealth", "ProtectionPaladin", "DeathKnight", "HolyPriest",
        "RogueThief", "ElementalShaman", "WildDruid", "SniperElite",
        "ChaosMaster", "LightBringer", "DarkSorcerer", "StormCaller"
    ]
    
    # Lista de guilds inimigas para batalhas
    enemy_guilds = [
        "Nightmare", "BlackOrder", "CrimsonTide", "ShadowLegion",
        "ImperialForce", "TitansBane", "VoidWalkers", "DragonsRoar", 
        "PhoenixRising", "FallenAngels"
    ]
    
    # Gerar batalhas para os últimos X dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    battles = []
    battle_count = random.randint(20, 40)  # Número aleatório de batalhas no período
    
    for i in range(battle_count):
        # Data e hora aleatória dentro do período
        battle_time = start_date + timedelta(
            days=random.randint(0, days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Determinar número de jogadores da guild nesta batalha
        guild_player_count = random.randint(10, len(guild_members))
        battle_players = random.sample(guild_members, guild_player_count)
        
        # Número de guilds inimigas nesta batalha (1-3)
        enemy_count = random.randint(1, min(3, len(enemy_guilds)))
        battle_enemies = random.sample(enemy_guilds, enemy_count)
        
        # Calcular estatísticas da guild
        guild_total_kills = 0
        guild_total_deaths = 0
        guild_total_fame = 0
        guild_players_stats = []
        
        for player in battle_players:
            # Gerar estatísticas para este jogador
            player_stats = generate_player_stats(player)
            guild_players_stats.append(player_stats)
            
            # Atualizar totais
            guild_total_kills += player_stats['kills']
            guild_total_deaths += player_stats['deaths']
            guild_total_fame += player_stats['fame']
        
        # Criar dados para as guilds inimigas
        enemy_guilds_stats = {}
        for enemy in battle_enemies:
            # Determinar número de jogadores inimigos
            enemy_player_count = random.randint(10, 25)
            enemy_total_kills = 0
            enemy_total_deaths = 0
            enemy_total_fame = 0
            enemy_players = []
            
            # Gerar nomes aleatórios para jogadores inimigos
            enemy_member_prefix = enemy[:3].upper()
            for j in range(enemy_player_count):
                enemy_player_name = f"{enemy_member_prefix}_Player{j+1}"
                
                # Estatísticas balanceadas para criar algumas vitórias e algumas derrotas
                if random.random() > 0.6:  # 40% chance de guild ganhar
                    # Guild ganha - inimigos têm menos kills, mais mortes
                    enemy_stats = generate_player_stats(
                        enemy_player_name, 
                        min_kills=0, max_kills=5,
                        min_deaths=3, max_deaths=12
                    )
                else:
                    # Guild perde - inimigos têm mais kills, menos mortes
                    enemy_stats = generate_player_stats(
                        enemy_player_name,
                        min_kills=3, max_kills=12,
                        min_deaths=0, max_deaths=5
                    )
                    
                enemy_players.append(enemy_stats)
                enemy_total_kills += enemy_stats['kills']
                enemy_total_deaths += enemy_stats['deaths']
                enemy_total_fame += enemy_stats['fame']
            
            # Adicionar esta guild inimiga
            enemy_guilds_stats[enemy] = {
                'players': enemy_players,
                'total_kills': enemy_total_kills,
                'total_deaths': enemy_total_deaths,
                'total_fame': enemy_total_fame
            }
        
        # Criar detalhes completos da batalha
        guilds_stats = {
            guild_name: {
                'players': guild_players_stats,
                'total_kills': guild_total_kills,
                'total_deaths': guild_total_deaths,
                'total_fame': guild_total_fame
            },
            **enemy_guilds_stats
        }
        
        battle_details = {
            'id': f"mock_battle_{i+1}",
            'time': battle_time,
            'guilds': guilds_stats
        }
        
        # Adicionar batalha à lista
        battles.append({
            'battle_id': f"mock_battle_{i+1}",
            'time': battle_time,
            'players': guild_player_count,
            'kills': guild_total_kills,
            'deaths': guild_total_deaths,
            'fame': guild_total_fame,
            'details': battle_details
        })
    
    # Converter para DataFrame e ordenar por data/hora
    battles_df = pd.DataFrame(battles)
    battles_df = battles_df.sort_values('time', ascending=False)
    
    return battles_df

def get_mock_battle_data(guild_name="We Profit", alliance_name="Baiah", days=30):
    """
    Retorna dados simulados de batalhas para testes quando a API não estiver funcionando
    """
    return generate_mock_battle_data(guild_name, alliance_name, days)