import requests
import pandas as pd
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ID da guild We Profit, já conhecida
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"

# URL direta conforme fornecida pelo usuário
API_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=20&sort=totalfame&guildId=gUFLG-kcRFC1iOJDdwW2BQ"

def get_battle_data():
    """
    Função simplificada para buscar e processar dados da API
    """
    try:
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        logging.info("Buscando dados da API...")
        response = requests.get(API_URL, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Erro HTTP {response.status_code}")
            return pd.DataFrame()
        
        # Carregar os dados como JSON
        battles_data = response.json()
        
        if not isinstance(battles_data, list):
            logging.error("Resposta não é uma lista de batalhas")
            return pd.DataFrame()
            
        logging.info(f"Obtidas {len(battles_data)} batalhas da API")
        
        # Processar batalhas
        processed_battles = []
        
        for battle in battles_data:
            try:
                # Extrair informações básicas
                battle_id = battle['id']
                battle_time = datetime.fromisoformat(battle['startTime'].replace('Z', '+00:00'))
                total_fame = battle['totalFame']
                
                # Filtrar jogadores da guild
                guild_players = [p for p in battle['players'] if p['guildId'] == GUILD_ID]
                
                if guild_players:
                    players_count = len(guild_players)
                    guild_kills = sum(p['kills'] for p in guild_players)
                    guild_deaths = sum(p['deaths'] for p in guild_players)
                    
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
                            'name': player['name'],
                            'kills': player['kills'],
                            'deaths': player['deaths'],
                            'fame': player['killFame']
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
        print(battles_df[['battle_id', 'kills', 'deaths']].head())