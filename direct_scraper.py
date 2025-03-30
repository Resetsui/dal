import requests
import trafilatura
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import streamlit as st

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    
    Args:
        url: The URL of the website to extract content from
        
    Returns:
        Text content of the website
    """
    # Send a request to the website
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text if text else ""

def scrape_battles(guild_id: str, days_back: int = 7) -> List[Dict]:
    """
    Scrape battle data for a specific guild from the Albion Online website.
    
    Args:
        guild_id: The ID of the guild to fetch battles for
        days_back: Number of days to look back
        
    Returns:
        List of battle data dictionaries
    """
    battles_url = f"https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=51&sort=totalfame&guildId={guild_id}"
    
    try:
        # Using requests to fetch the JSON data directly
        response = requests.get(battles_url)
        response.raise_for_status()
        
        # Parse the JSON response
        battles_data = response.json()
        return battles_data
    except Exception as e:
        st.error(f"Error scraping battles data: {str(e)}")
        return []

def scrape_battle_details(battle_id: str) -> Optional[Dict]:
    """
    Scrape detailed information for a specific battle from the Albion Online website.
    
    Args:
        battle_id: The ID of the battle to fetch details for
        
    Returns:
        Dictionary containing processed battle details or None if failed
    """
    battle_url = f"https://gameinfo.albiononline.com/api/gameinfo/battles/{battle_id}"
    
    try:
        # Fetch the battle details
        response = requests.get(battle_url)
        response.raise_for_status()
        
        # Parse the JSON response
        battle_data = response.json()
        
        # Process and organize battle data
        start_time = battle_data.get("startTime", 0)
        battle_time = datetime.now()  # Default fallback
        
        if isinstance(start_time, str):
            try:
                # First try converting string to int timestamp
                start_time = int(start_time)
                # If successful, convert timestamp to datetime
                if start_time > 0:
                    battle_time = datetime.utcfromtimestamp(start_time / 1000)
            except ValueError:
                # If can't convert to int, try to parse as ISO datetime
                try:
                    battle_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except ValueError:
                    pass  # Keep default fallback time
        else:
            # Direct integer timestamp
            try:
                if start_time > 0:
                    battle_time = datetime.utcfromtimestamp(start_time / 1000)
            except (ValueError, OverflowError):
                pass  # Keep default fallback time
                
        processed_data = {
            "battle_id": battle_id,
            "time": battle_time,
            "total_kills": battle_data.get("totalKills", 0),
            "total_fame": battle_data.get("totalFame", 0),
            "guilds": {},
            "players": {}
        }
        
        # Process players
        for player_id, player_data in battle_data.get("players", {}).items():
            player_name = player_data.get("name", "Unknown")
            guild_name = player_data.get("guildName", "No Guild")
            
            # Store player data
            processed_data["players"][player_name] = {
                "id": player_id,
                "guild": guild_name,
                "kills": player_data.get("kills", 0),
                "deaths": player_data.get("deaths", 0),
                "damage": player_data.get("damage", 0),
                "healing": player_data.get("healing", 0)
            }
            
            # Aggregate guild data
            if guild_name not in processed_data["guilds"]:
                processed_data["guilds"][guild_name] = {
                    "players": 0,
                    "kills": 0,
                    "deaths": 0,
                    "damage": 0,
                    "healing": 0,
                    "fame": 0
                }
            
            guild_stats = processed_data["guilds"][guild_name]
            guild_stats["players"] += 1
            guild_stats["kills"] += player_data.get("kills", 0)
            guild_stats["deaths"] += player_data.get("deaths", 0)
            guild_stats["damage"] += player_data.get("damage", 0)
            guild_stats["healing"] += player_data.get("healing", 0)
            guild_stats["fame"] += player_data.get("killFame", 0)
        
        return processed_data
        
    except Exception as e:
        st.error(f"Error scraping battle details: {str(e)}")
        return None

def scrape_guild_info(guild_id: str) -> Optional[Dict]:
    """
    Scrape guild information from the Albion Online website.
    
    Args:
        guild_id: The ID of the guild to fetch information for
        
    Returns:
        Dictionary with guild information or None if failed
    """
    guild_url = f"https://gameinfo.albiononline.com/api/gameinfo/guilds/{guild_id}"
    
    try:
        response = requests.get(guild_url)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        st.error(f"Error scraping guild information: {str(e)}")
        return None
