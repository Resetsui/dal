import json

# Carregar os dados da API
with open('test_api.json', 'r') as f:
    data = json.load(f)

# Analisar a primeira batalha
if data:
    battle = data[0]
    print(f"Batalha ID: {battle.get('id')}")
    print(f"Total kills: {battle.get('totalKills')}")
    print(f"Total fame: {battle.get('totalFame')}")
    
    # Extrair informações sobre guilds na batalha
    guilds = {}
    
    for player_id, player_data in battle.get('players', {}).items():
        guild_id = player_data.get('guildId')
        guild_name = player_data.get('guildName')
        
        if guild_id and guild_name:
            if guild_id not in guilds:
                guilds[guild_id] = {
                    'name': guild_name,
                    'kills': 0,
                    'deaths': 0,
                    'players': 0
                }
            
            guilds[guild_id]['kills'] += player_data.get('kills', 0)
            guilds[guild_id]['deaths'] += player_data.get('deaths', 0)
            guilds[guild_id]['players'] += 1
    
    # Mostrar informações sobre as guilds
    print("\nGuilds na batalha:")
    for guild_id, guild_info in guilds.items():
        print(f"- {guild_info['name']}: {guild_info['kills']} kills, {guild_info['deaths']} mortes, {guild_info['players']} jogadores")
else:
    print("Nenhum dado de batalha encontrado.")