import pandas as pd
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ID da guild We Profit, já conhecida
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"

def get_battle_data():
    """
    Função simples para ler os dados de batalha diretamente do arquivo JSON baixado
    """
    try:
        logging.info("Lendo dados do arquivo JSON temp.json")
        
        # Abrir o arquivo JSON que foi baixado separadamente
        with open('temp.json', 'r') as f:
            battle_json = f.read()
            
        # Converter para objeto Python
        battles_data = json.loads(battle_json)
        
        if not battles_data:
            logging.warning("Nenhum dado de batalha no arquivo")
            return pd.DataFrame()
        
        # Processar os dados de batalha diretamente
        processed_battles = []
        
        for battle in battles_data:
            try:
                battle_id = battle.get('id')
                battle_time_str = battle.get('startTime')
                if not battle_time_str:
                    continue
                    
                battle_time = datetime.fromisoformat(battle_time_str.replace('Z', '+00:00'))
                total_fame = battle.get('totalFame', 0)
                
                # Obter jogadores da guild
                players = battle.get('players', [])
                guild_players = []
                for player in players:
                    if player.get('guildId') == GUILD_ID:
                        guild_players.append(player)
                
                if guild_players:
                    players_count = len(guild_players)
                    guild_kills = sum(player.get('kills', 0) for player in guild_players)
                    guild_deaths = sum(player.get('deaths', 0) for player in guild_players)
                    
                    # Agrupar jogadores por guild para estatísticas de batalha
                    guilds_stats = {}
                    
                    for player in players:
                        player_guild_name = player.get('guildName', 'Unknown')
                        
                        if player_guild_name not in guilds_stats:
                            guilds_stats[player_guild_name] = {
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
                        
                        guilds_stats[player_guild_name]['players'].append(player_stats)
                        guilds_stats[player_guild_name]['total_kills'] += player_stats['kills']
                        guilds_stats[player_guild_name]['total_deaths'] += player_stats['deaths']
                        guilds_stats[player_guild_name]['total_fame'] += player_stats['fame']
                    
                    # Adicionar detalhes da batalha
                    battle_details = {
                        'id': battle_id,
                        'time': battle_time,
                        'guilds': guilds_stats
                    }
                    
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
                continue
                
        # Criar DataFrame
        battles_df = pd.DataFrame(processed_battles)
        logging.info(f"Processados dados de {len(battles_df)} batalhas com sucesso")
        
        return battles_df
    
    except Exception as e:
        logging.error(f"Erro ao processar dados: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Teste simples para verificar se a função está funcionando
    battles_df = get_battle_data()
    print(f"Encontradas {len(battles_df)} batalhas")