import pandas as pd
import numpy as np
import requests
import logging
import json
from datetime import datetime, timedelta
import time
from battle_history_manager import update_battle_history

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# API URLs for Albion Online official API
SEARCH_URL = "https://gameinfo.albiononline.com/api/gameinfo/search"
GUILD_URL = "https://gameinfo.albiononline.com/api/gameinfo/guilds"
BATTLES_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=51&sort=totalfame&guildId=gUFLG-kcRFC1iOJDdwW2BQ"
BATTLE_DETAIL_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles"  # Para buscar uma batalha específica, adicione /{battleId}

# Lista de IDs de batalhas conhecidas (para quando a API de listagem falhar)
# Estas são batalhas reais que já aconteceram e têm dados disponíveis
KNOWN_BATTLE_IDS = [
    "173256294", "173255407", "173254919", "173254596", "173254088",
    "173252884", "173252638", "173252169", "173251840", "173251429",
    "173251008", "173250742", "173250291", "173249971", "173248899"
]


def get_guild_id(guild_name, max_attempts=3, delay=2):
    """
    Get the guild ID from the Albion Online API by searching for a guild name
    """
    for attempt in range(max_attempts):
        try:
            # Prepare search parameters
            params = {"q": guild_name}

            # Make the API request with a longer timeout
            response = requests.get(SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Look for guilds in the search results
            if 'guilds' in data and data['guilds']:
                for guild in data['guilds']:
                    # Check if the guild name matches (case-insensitive)
                    if guild_name.lower() in guild['Name'].lower():
                        guild_id = guild['Id']
                        logging.info(
                            f"Found guild ID for {guild_name}: {guild_id}")
                        return guild_id

            # If we didn't find a match in this attempt
            logging.warning(
                f"Guild {guild_name} not found in attempt {attempt+1}/{max_attempts}"
            )

            # Wait before retrying (except on the last attempt)
            if attempt < max_attempts - 1:
                time.sleep(delay)

        except requests.exceptions.Timeout:
            logging.warning(
                f"Request timed out in attempt {attempt+1}/{max_attempts}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error searching for guild: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

    # If we reach here, we couldn't find the guild after all attempts
    logging.warning(
        f"Guild {guild_name} not found after {max_attempts} attempts")
    return None


def get_guild_battles(guild_id, days=7, max_attempts=8, delay=5):
    """
    Get battles for a specific guild from the Albion Online API
    """
    if not guild_id:
        return pd.DataFrame()

    battles = []
    for attempt in range(max_attempts):
        try:
            # Usar o formato exato da URL fornecido pelo usuário
            # URL exata fornecida pelo usuário
            url = f"https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=51&sort=totalfame&guildId={guild_id}"

            # Se precisar de mais dias, modifique o parâmetro range
            if days > 14:
                url = url.replace("range=week", "range=month")
            elif days > 7:
                url = url.replace("range=week", "range=2weeks")

            # Adicionar headers para simular um navegador
            headers = {
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://albiononline.com/'
            }

            logging.info(
                f"Tentativa {attempt+1}/{max_attempts} de obter dados de batalhas usando a URL direta: {url}"
            )
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse the battles data and ensure it's a list
            battles_data = response.json()

            # Log para debug
            logging.info(f"Resposta da API: {battles_data}")

            if isinstance(battles_data, dict):
                if 'error' in battles_data:
                    logging.error(f"Erro da API: {battles_data['error']}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue

            if not isinstance(battles_data, list):
                if isinstance(battles_data, dict):
                    # Se for um dicionário, pode estar em outro formato
                    logging.info("Convertendo formato da resposta")
                    battles_data = [battles_data]
                else:
                    logging.error(f"Resposta da API em formato inesperado: {type(battles_data)}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue

            if not battles_data:
                logging.warning("Lista de batalhas vazia")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                continue

            logging.info(f"Recebidas {len(battles_data)} batalhas da API")

            # Process each battle
            for battle in battles_data:
                # Basic battle info
                battle_id = battle.get('id')
                battle_time = datetime.fromisoformat(
                    battle.get('startTime').replace('Z', '+00:00'))
                total_kills = battle.get('totalKills', 0)
                total_fame = battle.get('totalFame', 0)

                # Process players from this guild in the battle
                players_count = 0
                guild_kills = 0
                guild_deaths = 0

                # Look through all players in the battle
                guild_players = [
                    player for player in battle.get('players', [])
                    if player.get('guildId') == guild_id
                ]

                if guild_players:
                    players_count = len(guild_players)
                    guild_kills = sum(
                        player.get('kills', 0) for player in guild_players)
                    guild_deaths = sum(
                        player.get('deaths', 0) for player in guild_players)

                    battles.append({
                        'battle_id': battle_id,
                        'time': battle_time,
                        'players': players_count,
                        'kills': guild_kills,
                        'deaths': guild_deaths,
                        'fame': total_fame,
                        'raw_data': battle
                    })

            # Convert to DataFrame
            battles_df = pd.DataFrame(battles)
            logging.info(
                f"Retrieved {len(battles_df)} battles for guild ID {guild_id}")

            if not battles_df.empty:
                return battles_df
            else:
                logging.warning(f"No battles found for guild ID {guild_id}")
                # Try again if no battles found
                if attempt < max_attempts - 1:
                    time.sleep(delay)

        except requests.exceptions.Timeout:
            logging.warning(
                f"Request timed out in attempt {attempt+1}/{max_attempts}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting battles: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

        except Exception as e:
            logging.error(f"Unexpected error processing battles: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

    # If we reach here, we couldn't get battles after all attempts
    return pd.DataFrame()


def process_battle_details(battle_data, guild_name):
    """
    Extract detailed information from battle data
    """
    if not battle_data or 'raw_data' not in battle_data:
        return None

    # Debug log para verificar o formato dos dados recebidos
    logging.info(
        f"Processando detalhes da batalha: {battle_data['battle_id']}")

    # Verificar se raw_data é uma string (resposta da API) ou um dicionário
    raw_battle = battle_data['raw_data']
    if isinstance(raw_battle, str):
        try:
            raw_battle = json.loads(raw_battle)
        except Exception as e:
            logging.error(f"Erro ao converter raw_data para JSON: {e}")
            return None

    battle_id = battle_data['battle_id']
    battle_time = battle_data['time']

    # Prepare the guild stats dictionary
    guilds_stats = {}

    # Group players by guild
    guilds = {}
    for player in raw_battle.get('players', []):
        guild_id = player.get('guildId')
        guild_name_api = player.get('guildName', 'Unknown')

        if guild_id not in guilds:
            guilds[guild_id] = {
                'name': guild_name_api,
                'players': [],
                'total_kills': 0,
                'total_deaths': 0,
                'total_fame': 0
            }

        # Add player data
        player_stats = {
            'name': player.get('name', 'Unknown'),
            'kills': player.get('kills', 0),
            'deaths': player.get('deaths', 0),
            'fame': player.get('killFame', 0)
        }

        guilds[guild_id]['players'].append(player_stats)
        guilds[guild_id]['total_kills'] += player_stats['kills']
        guilds[guild_id]['total_deaths'] += player_stats['deaths']
        guilds[guild_id]['total_fame'] += player_stats['fame']

    # Format guilds for the return structure
    for guild_id, stats in guilds.items():
        guilds_stats[stats['name']] = {
            'players': stats['players'],
            'total_kills': stats['total_kills'],
            'total_deaths': stats['total_deaths'],
            'total_fame': stats['total_fame']
        }

    battle_details = {
        'id': battle_id,
        'time': battle_time,
        'guilds': guilds_stats
    }

    return battle_details


def get_battle_by_id(battle_id, max_attempts=3, delay=2):
    """
    Get a specific battle by ID directly from the API
    """
    url = f"{BATTLE_DETAIL_URL}/{battle_id}"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    for attempt in range(max_attempts):
        try:
            logging.info(
                f"Buscando batalha ID {battle_id}, tentativa {attempt+1}/{max_attempts}"
            )
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            battle_data = response.json()

            # Verificar se a resposta possui o formato esperado
            if 'id' not in battle_data:
                logging.warning(
                    f"Resposta para batalha ID {battle_id} não possui o formato esperado"
                )
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                continue

            battle_id = battle_data.get('id')
            battle_time = datetime.fromisoformat(
                battle_data.get('startTime').replace('Z', '+00:00'))

            return {
                'battle_id': battle_id,
                'time': battle_time,
                'raw_data': battle_data
            }

        except requests.exceptions.Timeout:
            logging.warning(
                f"Timeout ao buscar batalha ID {battle_id}, tentativa {attempt+1}/{max_attempts}"
            )
            if attempt < max_attempts - 1:
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar batalha ID {battle_id}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)

    return None


def refresh_battle_data(guild_name, days=30):
    """
    Refresh all battle data for a guild using the Albion Online API
    """
    logging.info(f"Refreshing battle data for {guild_name}")

    # O ID da guild "We Profit" nos foi fornecido diretamente pelo usuário
    if guild_name == "We Profit":
        guild_id = "gUFLG-kcRFC1iOJDdwW2BQ"
        logging.info(f"Usando ID fixo para guild We Profit: {guild_id}")
    else:
        # Para outras guilds, tentamos procurar pelo nome
        guild_id = get_guild_id(guild_name)

    if not guild_id:
        logging.warning(
            f"Guild ID não encontrado para {guild_name}, tentando usar batalhas conhecidas"
        )
        return get_known_battles(guild_name)

    # Get basic battle information
    battles_df = get_guild_battles(guild_id, days)

    # Se não conseguir obter batalhas pela API normal, tentar com IDs conhecidos
    if battles_df.empty:
        logging.warning(
            "Não foi possível obter batalhas pela API padrão, tentando com batalhas conhecidas"
        )
        return get_known_battles(guild_name)

    # Process battle details
    detailed_battles = []

    for _, battle in battles_df.iterrows():
        battle_details = process_battle_details(battle, guild_name)

        if battle_details:
            detailed_battles.append({
                'battle_id': battle['battle_id'],
                'time': battle['time'],
                'players': battle['players'],
                'kills': battle['kills'],
                'deaths': battle['deaths'],
                'fame': battle['fame'],
                'details': battle_details
            })

    # Create detailed DataFrame
    detailed_df = pd.DataFrame(detailed_battles)
    logging.info(f"Retrieved detailed data for {len(detailed_df)} battles")

    # Atualizar o histórico de batalhas com os novos dados
    if not detailed_df.empty:
        try:
            update_battle_history(detailed_df)
            logging.info(
                f"Histórico de batalhas atualizado com {len(detailed_df)} novas batalhas"
            )
        except Exception as e:
            logging.error(f"Erro ao atualizar histórico de batalhas: {e}")

    return detailed_df


def get_known_battles(guild_name):
    """
    Use known battle IDs to get battle data when the regular API fails
    """
    detailed_battles = []

    # Buscar até 5 batalhas conhecidas
    for battle_id in KNOWN_BATTLE_IDS[:5]:
        battle = get_battle_by_id(battle_id)
        if not battle:
            continue

        # Processar detalhes da batalha para extrair dados relevantes
        battle_details = process_battle_details(battle, guild_name)

        if battle_details:
            # Verificar se a guild solicitada participa desta batalha
            guild_found = False
            for guild, stats in battle_details['guilds'].items():
                if guild_name.lower() in guild.lower():
                    guild_found = True
                    players_count = len(stats['players'])
                    guild_kills = stats['total_kills']
                    guild_deaths = stats['total_deaths']

                    detailed_battles.append({
                        'battle_id': battle['battle_id'],
                        'time': battle['time'],
                        'players': players_count,
                        'kills': guild_kills,
                        'deaths': guild_deaths,
                        'fame': stats['total_fame'],
                        'details': battle_details
                    })
                    break

            # Se a guild não está nesta batalha e já temos algumas batalhas, talvez seja uma boa hora para parar
            if not guild_found and len(detailed_battles) >= 3:
                break

    # Criar DataFrame com batalhas encontradas
    detailed_df = pd.DataFrame(
        detailed_battles) if detailed_battles else pd.DataFrame()
    logging.info(
        f"Retrieved {len(detailed_df)} battles using known battle IDs")

    # Atualizar o histórico de batalhas com os novos dados
    if not detailed_df.empty:
        try:
            update_battle_history(detailed_df)
            logging.info(
                f"Histórico de batalhas atualizado com {len(detailed_df)} batalhas conhecidas"
            )
        except Exception as e:
            logging.error(
                f"Erro ao atualizar histórico de batalhas com batalhas conhecidas: {e}"
            )

    return detailed_df