import requests
import pandas as pd
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL fornecida diretamente pelo usuário - a fonte única de verdade
BATTLES_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=20&sort=totalfame&guildId=gUFLG-kcRFC1iOJDdwW2BQ"

def get_battle_data():
    """
    Função simples para buscar dados de batalha diretamente da URL fornecida pelo usuário
    """
    try:
        # Configuração adequada do request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://albiononline.com/'
        }
        
        logging.info(f"Buscando dados de batalhas diretamente da URL: {BATTLES_URL}")
        response = requests.get(BATTLES_URL, headers=headers, timeout=10)
        
        # Verificar resposta
        if response.status_code != 200:
            logging.error(f"Erro na resposta HTTP: {response.status_code}")
            return pd.DataFrame()
        
        # Salvar dados brutos em um arquivo para depuração
        with open('raw_battles_data.json', 'w') as f:
            f.write(response.text)
            
        logging.info("Dados salvos com sucesso em raw_battles_data.json")
        
        # Verificar se a resposta é um array de objetos JSON ou um único objeto
        if response.text.strip().startswith('['):
            battles_data = response.json()  # É um array de batalhas
        else:
            # Pode ser uma resposta em string ou formato HTML em vez de JSON
            logging.warning("A resposta não é um array. Tentando analisar como objeto único.")
            try:
                battle_obj = response.json()
                if isinstance(battle_obj, dict):
                    # Convertemos para lista com um único objeto
                    battles_data = [battle_obj]
                else:
                    logging.error("Formato de resposta não reconhecido")
                    return pd.DataFrame()
            except json.JSONDecodeError:
                logging.error("A resposta não é um JSON válido")
                return pd.DataFrame()
        
        if not battles_data:
            logging.warning("Nenhum dado de batalha retornado")
            return pd.DataFrame()
        
        # Processar os dados de batalha diretamente
        processed_battles = []
        guild_id = "gUFLG-kcRFC1iOJDdwW2BQ"  # ID da guild We Profit
        guild_name = "We Profit"
        
        for battle in battles_data:
            battle_id = battle.get('id')
            battle_time = datetime.fromisoformat(battle.get('startTime').replace('Z', '+00:00'))
            total_fame = battle.get('totalFame', 0)
            
            # Filtrar jogadores da guild
            guild_players = [player for player in battle.get('players', []) if player.get('guildId') == guild_id]
            
            if guild_players:
                players_count = len(guild_players)
                guild_kills = sum(player.get('kills', 0) for player in guild_players)
                guild_deaths = sum(player.get('deaths', 0) for player in guild_players)
                
                # Agrupar jogadores por guild para estatísticas de batalha
                guilds_stats = {}
                all_players = battle.get('players', [])
                
                for player in all_players:
                    player_guild_id = player.get('guildId')
                    player_guild_name = player.get('guildName', 'Unknown')
                    
                    if player_guild_id not in guilds_stats:
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
                
        # Criar DataFrame
        battles_df = pd.DataFrame(processed_battles)
        logging.info(f"Processados dados de {len(battles_df)} batalhas com sucesso")
        
        return battles_df
    
    except requests.exceptions.Timeout:
        logging.error("Timeout ao buscar dados da API")
        return pd.DataFrame()
    
    except Exception as e:
        logging.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Teste simples para verificar se a função está funcionando
    battles_df = get_battle_data()
    print(f"Encontradas {len(battles_df)} batalhas")