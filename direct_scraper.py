# Check if the function exists in direct_scraper.py
# If not, we'll need to add it

def get_battle_data(user_id=None, battle_id=None):
    """
    Retrieves battle data for a specific user or battle.
    
    Args:
        user_id (str, optional): The ID of the user to get battles for
        battle_id (str, optional): The specific battle ID to retrieve
        
    Returns:
        dict: Battle data in JSON format
    """
    # Implement the actual battle data retrieval logic here
    # This is a placeholder implementation
    
    import json
    import os
    
    # Check if battle_history.json exists and load data from it
    if os.path.exists('battle_history.json'):
        with open('battle_history.json', 'r') as f:
            try:
                battle_data = json.load(f)
                
                # Filter by battle_id if provided
                if battle_id and isinstance(battle_data, list):
                    for battle in battle_data:
                        if battle.get('id') == battle_id:
                            return battle
                    return {"error": "Battle not found"}
                
                # Filter by user_id if provided
                if user_id and isinstance(battle_data, list):
                    user_battles = [b for b in battle_data if b.get('user_id') == user_id]
                    return user_battles
                
                return battle_data
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in battle_history.json"}
    
    # Return empty data if file doesn't exist
    return {"error": "No battle data available"}
