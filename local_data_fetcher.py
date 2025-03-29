import pandas as pd
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ID da guild We Profit, já conhecida
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"

# Arquivo local com dados baixados previamente
DATA_FILE = "data.json"

def get_battle_data():
    """
    Função para processar dados de batalha armazenados localmente
    """
    try:
        logging.info(f"Lendo dados de batalhas do arquivo local: {DATA_FILE}")
        
        # Abrir o arquivo JSON
        with open(DATA_FILE, 'r') as f:
            battles_data = json.load(f)
        
        logging.info(f"Encontrados dados de {len(battles_data)} batalhas no arquivo")
        
        # Processar batalhas
        processed_battles = []
        
        for battle in battles_data:
            try:
                # Extrair informações básicas
                battle_id = battle['id']
                battle_time = datetime.fromisoformat(battle['startTime'].replace('Z', '+00:00'))
                total_fame = battle['totalFame']
                
                # Filtrar jogadores da guild
                guild_players = [p for p in battle['players'] if p.get('guildId') == GUILD_ID]
                
                if guild_players:
                    players_count = len(guild_players)
                    guild_kills = sum(p.get('kills', 0) for p in guild_players)
                    guild_deaths = sum(p.get('deaths', 0) for p in guild_players)
                    
                    # Agrupar por guild
                    guilds_stats = {}
                    
                    for player in battle['players']:
                        guild_name = player.get('guildName', 'Unknown')
                        
                        if guild_name not in guilds_stats:
                            guilds_stats[guild_name] = {
                                'players': [],
                                'total_kills': 0,
                                'total_deaths': 0,
                                'total_fame': 0
                            }
                        
                        player_stats = {
                            'name': player.get('name', 'Unknown'),
                            'kills': player.get('kills', 0),
                            'deaths': player.get('deaths', 0),
                            'fame': player.get('killFame', 0)
                        }
                        
                        guilds_stats[guild_name]['players'].append(player_stats)
                        guilds_stats[guild_name]['total_kills'] += player_stats['kills']
                        guilds_stats[guild_name]['total_deaths'] += player_stats['deaths']
                        guilds_stats[guild_name]['total_fame'] += player_stats['fame']
                    
                    # Criar objeto de detalhes
                    battle_details = {
                        'id': battle_id,
                        'time': battle_time,
                        'guilds': guilds_stats
                    }
                    
                    # Adicionar à lista
                    processed_battles.append({
                        'battle_id': battle_id,
                        'time': battle_time,
                        'players': players_count,
                        'kills': guild_kills,
                        'deaths': guild_deaths,
                        'fame': total_fame,
                        'details': battle_details
                    })
            except Exception as e:
                logging.error(f"Erro ao processar batalha: {e}")
        
        # Criar DataFrame
        battles_df = pd.DataFrame(processed_battles)
        logging.info(f"Processados dados de {len(battles_df)} batalhas com sucesso")
        
        return battles_df
    
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Teste direto
    battles_df = get_battle_data()
    print(f"Encontradas {len(battles_df)} batalhas")
    if not battles_df.empty:
        print("\nPrimeiras batalhas:")
        print(battles_df[['battle_id', 'kills', 'deaths']].head())
        
        print("\nEstatísticas da guild:")
        print(f"Total de kills: {battles_df['kills'].sum()}")
        print(f"Total de mortes: {battles_df['deaths'].sum()}")
        print(f"K/D ratio: {battles_df['kills'].sum() / max(1, battles_df['deaths'].sum()):.2f}")