import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for albionbattles.com
BASE_URL = "https://albionbattles.com"
GUILD_SEARCH_URL = f"{BASE_URL}/guilds"
BATTLES_URL = f"{BASE_URL}/battles"

def get_guild_id(guild_name):
    """Get the guild ID for a given guild name from albionbattles.com"""
    try:
        # Search for the guild
        params = {"q": guild_name}
        response = requests.get(GUILD_SEARCH_URL, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        guild_links = soup.select('a[href^="/guilds/"]')
        
        for link in guild_links:
            if guild_name.lower() in link.text.lower():
                guild_id = link['href'].split('/')[-1]
                logging.info(f"Found guild ID for {guild_name}: {guild_id}")
                return guild_id
        
        logging.warning(f"Guild {guild_name} not found")
        return None
    
    except Exception as e:
        logging.error(f"Error getting guild ID: {e}")
        return None

def get_guild_battles(guild_id, days=7):
    """Get battles for a specific guild from albionbattles.com"""
    if not guild_id:
        return pd.DataFrame()
    
    try:
        guild_battles_url = f"{BASE_URL}/guilds/{guild_id}"
        response = requests.get(guild_battles_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        battles_table = soup.select_one('table.table-battles')
        
        if not battles_table:
            logging.warning(f"No battles table found for guild ID {guild_id}")
            return pd.DataFrame()
        
        # Parse battles from the table
        battles = []
        rows = battles_table.select('tbody tr')
        
        for row in rows:
            try:
                cols = row.select('td')
                if len(cols) < 6:
                    continue
                
                # Extract battle ID from the link
                battle_link = cols[0].select_one('a')
                if not battle_link:
                    continue
                
                battle_id = battle_link['href'].split('/')[-1]
                
                # Extract battle time
                time_str = cols[0].text.strip()
                battle_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                
                # Check if battle is within the specified days
                if battle_time < datetime.now() - timedelta(days=days):
                    continue
                
                # Extract other battle information
                players = int(cols[1].text.strip())
                kills = int(cols[2].text.strip())
                deaths = int(cols[3].text.strip())
                fame = int(cols[4].text.strip().replace(',', ''))
                
                battles.append({
                    'battle_id': battle_id,
                    'time': battle_time,
                    'players': players,
                    'kills': kills,
                    'deaths': deaths,
                    'fame': fame
                })
            
            except Exception as e:
                logging.error(f"Error parsing battle row: {e}")
                continue
        
        battles_df = pd.DataFrame(battles)
        logging.info(f"Retrieved {len(battles_df)} battles for guild ID {guild_id}")
        return battles_df
    
    except Exception as e:
        logging.error(f"Error getting guild battles: {e}")
        return pd.DataFrame()

def get_battle_details(battle_id):
    """Get detailed information about a specific battle"""
    if not battle_id:
        return None
    
    try:
        battle_url = f"{BATTLES_URL}/{battle_id}"
        response = requests.get(battle_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get battle time and title
        battle_time_elem = soup.select_one('h4.card-title')
        battle_time = None
        if battle_time_elem:
            time_str = battle_time_elem.text.strip()
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', time_str)
            if time_match:
                battle_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
        
        # Get battle stats
        guild_stats = {}
        guild_tables = soup.select('div.card-body table.table-responsive')
        
        for table in guild_tables:
            guild_header = table.select_one('th[colspan]')
            if not guild_header:
                continue
            
            guild_name = guild_header.text.strip()
            guild_stats[guild_name] = {
                'players': [],
                'total_kills': 0,
                'total_deaths': 0,
                'total_fame': 0
            }
            
            player_rows = table.select('tbody tr')
            for row in player_rows:
                cols = row.select('td')
                if len(cols) < 5:
                    continue
                
                player_name = cols[0].text.strip()
                kills = int(cols[1].text.strip())
                deaths = int(cols[2].text.strip())
                fame = int(cols[3].text.strip().replace(',', ''))
                
                guild_stats[guild_name]['players'].append({
                    'name': player_name,
                    'kills': kills,
                    'deaths': deaths,
                    'fame': fame
                })
                
                guild_stats[guild_name]['total_kills'] += kills
                guild_stats[guild_name]['total_deaths'] += deaths
                guild_stats[guild_name]['total_fame'] += fame
        
        battle_details = {
            'id': battle_id,
            'time': battle_time,
            'guilds': guild_stats
        }
        
        return battle_details
    
    except Exception as e:
        logging.error(f"Error getting battle details: {e}")
        return None

def refresh_battle_data(guild_name, days=30):
    """Refresh all battle data for a guild"""
    logging.info(f"Refreshing battle data for {guild_name}")
    
    # Get guild ID
    guild_id = get_guild_id(guild_name)
    if not guild_id:
        return pd.DataFrame()
    
    # Get basic battle information
    battles_df = get_guild_battles(guild_id, days)
    if battles_df.empty:
        return pd.DataFrame()
    
    # Retrieve detailed information for each battle
    detailed_battles = []
    
    # Progress bar for battle fetching
    progress_bar = None
    if st.session_state.get('is_refreshing', False):
        progress_bar = st.progress(0)
    
    for i, (_, battle) in enumerate(battles_df.iterrows()):
        battle_id = battle['battle_id']
        
        # Update progress if bar exists
        if progress_bar:
            progress_bar.progress((i + 1) / len(battles_df))
        
        # Get detailed battle information
        battle_details = get_battle_details(battle_id)
        if battle_details:
            detailed_battles.append({
                'battle_id': battle_id,
                'time': battle['time'],
                'players': battle['players'],
                'kills': battle['kills'],
                'deaths': battle['deaths'],
                'fame': battle['fame'],
                'details': battle_details
            })
        
        # Be nice to the server and avoid rate limiting
        time.sleep(0.5)
    
    # Clear progress bar
    if progress_bar:
        progress_bar.empty()
    
    # Create detailed DataFrame
    detailed_df = pd.DataFrame(detailed_battles)
    logging.info(f"Retrieved detailed data for {len(detailed_df)} battles")
    
    return detailed_df
