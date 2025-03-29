import requests
import pandas as pd
from datetime import datetime
import logging
import json
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BATTLES_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=51&sort=totalfame&guildId=gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"

def get_battle_data(force_refresh=False):
    try:
        if not force_refresh:
            try:
                with open('data.json', 'r') as f:
                    response = json.load(f)
                logging.info("Dados carregados do arquivo local")
            except:
                logging.info("Arquivo local não encontrado, buscando da API")
                response = requests.get(BATTLES_URL).json()
                with open('data.json', 'w') as f:
                    json.dump(response, f)
        else:
            response = requests.get(BATTLES_URL).json()
            with open('data.json', 'w') as f:
                json.dump(response, f)

        processed_battles = []

        for battle in response:
            try:
                guild_players = []
                guild_kills = 0
                guild_deaths = 0
                guild_fame = 0
                
                # Coletar informações de todas as guilds
                guilds_info = {}
                enemy_guilds = {}
                alliance_guilds = {}
                
                # Nome da aliança para identificação
                ALLIANCE_NAME = "BAHlA"

                # Processar jogadores
                for player_id, player_data in battle.get('players', {}).items():
                    guild_id = player_data.get('guildId')
                    guild_name = player_data.get('guildName', '')
                    alliance_name = player_data.get('allianceName', '')
                    
                    if guild_id:
                        # Se for da nossa guild, registre os jogadores individualmente
                        if guild_id == GUILD_ID:
                            player_kills = player_data.get('kills', 0)
                            player_deaths = player_data.get('deaths', 0)
                            player_fame = player_data.get('killFame', 0)
                            
                            guild_players.append({
                                'name': player_data.get('name'),
                                'kills': player_kills,
                                'deaths': player_deaths,
                                'fame': player_fame
                            })
                            
                            guild_kills += player_kills
                            guild_deaths += player_deaths
                            guild_fame += player_fame
                        # Se for da nossa aliança, mas não da nossa guild
                        elif alliance_name and alliance_name.upper() == ALLIANCE_NAME.upper():
                            player_kills = player_data.get('kills', 0)
                            player_deaths = player_data.get('deaths', 0)
                            alliance_id = player_data.get('allianceId', '')
                            
                            # Inicializar a estrutura da guild aliada se não existir
                            if guild_id not in alliance_guilds:
                                alliance_guilds[guild_id] = {
                                    'name': guild_name,
                                    'players': 0,
                                    'kills': 0,
                                    'deaths': 0,
                                    'alliance_id': alliance_id,
                                    'alliance_name': alliance_name
                                }
                            
                            current_guild = alliance_guilds[guild_id]
                            current_guild['players'] += 1
                            current_guild['kills'] += player_kills
                            current_guild['deaths'] += player_deaths
                        else:
                            # Registrar guilds inimigas
                            player_kills = player_data.get('kills', 0)
                            player_deaths = player_data.get('deaths', 0)
                            
                            # Inicializar a estrutura da guild inimiga se não existir
                            if guild_id not in enemy_guilds:
                                enemy_guilds[guild_id] = {
                                    'name': guild_name,
                                    'players': 0,
                                    'kills': 0,
                                    'deaths': 0
                                }
                            
                            current_guild = enemy_guilds[guild_id]
                            current_guild['players'] += 1
                            current_guild['kills'] += player_kills
                            current_guild['deaths'] += player_deaths

                if guild_players:  # Só adicionar batalhas com jogadores da guild
                    battle_id = battle.get('id')
                    battle_time = datetime.fromisoformat(battle.get('startTime').replace('Z', '+00:00'))
                    
                    # Encontrar a guild inimiga principal (mais jogadores ou mais kills)
                    main_enemy = {'name': '', 'players': 0, 'kills': 0}
                    for guild_id, guild_data in enemy_guilds.items():
                        if guild_data['players'] > main_enemy['players'] or \
                           (guild_data['players'] == main_enemy['players'] and guild_data['kills'] > main_enemy['kills']):
                            main_enemy = guild_data
                    
                    # Construir o dicionário de guilds para os detalhes da batalha
                    battle_guilds = {
                        'We Profit': {
                            'players': guild_players,
                            'total_kills': guild_kills,
                            'total_deaths': guild_deaths,
                            'total_fame': guild_fame
                        }
                    }
                    
                    # Adicionar informações sobre as guilds inimigas com pelo menos 10 jogadores
                    for guild_id, guild_data in enemy_guilds.items():
                        if guild_data['players'] >= 10:  # Apenas adicionar guilds com número significativo de jogadores
                            # Criamos "jogadores falsos" para manter a contagem correta
                            fake_players = [{'name': 'player'} for _ in range(guild_data['players'])]
                            
                            battle_guilds[guild_data['name']] = {
                                'players': fake_players,  # Lista de jogadores fictícios para manter a contagem correta
                                'total_kills': guild_data['kills'],
                                'total_deaths': guild_data['deaths'],
                                'total_fame': 0,  # Não processamos a fama por jogador para guilds inimigas
                                'player_count': guild_data['players']  # Adicionamos também a contagem direta
                            }
                    
                    # Adicionar informações sobre as guilds da aliança
                    for guild_id, guild_data in alliance_guilds.items():
                        # Criamos "jogadores falsos" para manter a contagem correta
                        fake_players = [{'name': 'player'} for _ in range(guild_data['players'])]
                        
                        battle_guilds[guild_data['name']] = {
                            'players': fake_players,
                            'total_kills': guild_data['kills'],
                            'total_deaths': guild_data['deaths'],
                            'total_fame': 0,
                            'player_count': guild_data['players'],
                            'alliance': True,  # Marcar como guild da aliança
                            'alliance_id': guild_data.get('alliance_id', ''),
                            'alliance_name': guild_data.get('alliance_name', 'BAHlA')
                        }
                    
                    # Structure battle data with guilds information
                    battle_details = {
                        'battle_id': battle_id,
                        'time': battle_time,
                        'players': len(guild_players),
                        'kills': guild_kills,
                        'deaths': guild_deaths,
                        'fame': guild_fame,
                        'enemy': main_enemy['name'],  # Adicionando o nome da guild inimiga principal
                        'details': {
                            'id': battle_id,
                            'time': battle_time,
                            'guilds': battle_guilds,
                            'totalKills': battle.get('totalKills'),
                            'totalFame': battle.get('totalFame')
                        }
                    }
                    processed_battles.append(battle_details)
            except Exception as e:
                logging.error(f"Erro ao processar batalha {battle.get('id')}: {str(e)}")
                continue

        battles_df = pd.DataFrame(processed_battles)
        logging.info(f"Processadas {len(battles_df)} batalhas")
        return battles_df

    except Exception as e:
        logging.error(f"Erro ao processar dados: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_battle_data(force_refresh=True)
    print(f"Batalhas encontradas: {len(df)}")