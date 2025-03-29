import pandas as pd
import json
import logging
from datetime import datetime
import os
from battle_history_manager import update_battle_history, load_battle_history, get_battles_by_timeframe
from api_scraper import refresh_battle_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ID da guild We Profit, já conhecida
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"

# Arquivo local com dados baixados previamente
DATA_FILE = "data.json"

def process_raw_battle_data(battles_data):
    """
    Processa dados brutos de batalhas para o formato padronizado
    """
    processed_battles = []
    
    for battle in battles_data:
        try:
            # Extrair informações básicas
            battle_id = battle['id']
            battle_time = datetime.fromisoformat(battle['startTime'].replace('Z', '+00:00'))
            total_fame = battle['totalFame']
            
            # Os jogadores estão organizados como um dicionário, onde as chaves são os IDs dos jogadores
            players_dict = battle['players']
            all_players = list(players_dict.values())
            
            # Filtrar jogadores da guild
            guild_players = [p for p in all_players if p.get('guildId') == GUILD_ID]
            
            if guild_players:
                players_count = len(guild_players)
                guild_kills = sum(p.get('kills', 0) for p in guild_players)
                guild_deaths = sum(p.get('deaths', 0) for p in guild_players)
                
                # Agrupar por guild
                guilds_stats = {}
                
                for player in all_players:
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
            logging.error(f"Erro ao processar batalha {battle.get('id', 'unknown')}: {e}")
    
    # Criar DataFrame
    return pd.DataFrame(processed_battles)

def get_battle_data(days=None, force_refresh=False):
    """
    Função para processar dados de batalha, combinando dados recentes com histórico
    
    Args:
        days: Número de dias no passado para recuperar dados (None = todos)
        force_refresh: Se True, força a busca de dados na API em vez de usar dados locais
    
    Returns:
        DataFrame com dados de batalhas
    """
    try:
        # Se force_refresh é True, buscamos dados atualizados da API
        if force_refresh:
            logging.info(f"Forçando atualização de dados da API para os últimos {days if days else 30} dias")
            api_days = days if days is not None else 30
            battles_df = refresh_battle_data(GUILD_NAME, days=api_days)
            
            if not battles_df.empty:
                logging.info(f"Dados atualizados com sucesso via API: {len(battles_df)} batalhas")
                # Já que refresh_battle_data já atualiza o histórico, apenas retornamos os dados
                return battles_df
            else:
                logging.warning("Não foi possível atualizar dados via API, usando dados locais")
        
        # Processamento padrão dos dados locais
        if os.path.exists(DATA_FILE):
            logging.info(f"Lendo dados de batalhas do arquivo local: {DATA_FILE}")
            
            # Abrir o arquivo JSON
            with open(DATA_FILE, 'r') as f:
                battles_data = json.load(f)
            
            logging.info(f"Encontrados dados de {len(battles_data)} batalhas no arquivo")
            
            # Processar os dados brutos
            new_battles_df = process_raw_battle_data(battles_data)
            logging.info(f"Processados dados de {len(new_battles_df)} batalhas com sucesso")
            
            # Atualizar o histórico com as novas batalhas
            update_battle_history(new_battles_df)
        else:
            logging.warning(f"Arquivo de dados {DATA_FILE} não encontrado")
        
        # Retornar os dados históricos filtrados pelo período solicitado
        if days is not None:
            battles_df = get_battles_by_timeframe(days)
            logging.info(f"Retornando {len(battles_df)} batalhas dos últimos {days} dias")
        else:
            battles_df = load_battle_history()
            logging.info(f"Retornando todas as {len(battles_df)} batalhas do histórico")
        
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