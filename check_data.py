import json

# Carregar os dados brutos
with open('data.json', 'r') as f:
    data = json.load(f)

print(f"Total de batalhas: {len(data)}")

# Verificar a primeira batalha
first_battle = data[0]
print("\nDados da primeira batalha:")
print(f"ID: {first_battle.get('id')}")
print(f"Data: {first_battle.get('startTime')}")
print(f"Total de jogadores: {len(first_battle.get('players', {}))}")

# Verificar se existe allianceName e allianceId
alliance_players = []
for player_id, player in first_battle.get('players', {}).items():
    alliance_name = player.get('allianceName')
    alliance_id = player.get('allianceId')
    if alliance_name and alliance_id:
        alliance_players.append({
            'name': player.get('name'),
            'guild': player.get('guildName'),
            'alliance_name': alliance_name,
            'alliance_id': alliance_id
        })

print(f"\nJogadores com informação de aliança: {len(alliance_players)}")
if alliance_players:
    print("\nExemplo de jogador com aliança:")
    print(json.dumps(alliance_players[0], indent=2))
else:
    print("Nenhum jogador com aliança encontrado")

# Vamos verificar os dados processados pelo direct_scraper
try:
    with open('battle_history.json', 'r') as f:
        history_data = json.load(f)
    
    print(f"\nTotal de batalhas no histórico: {len(history_data)}")
    
    if history_data:
        # Verificar uma batalha processada
        first_processed = history_data[0]
        print("\nDados de uma batalha processada:")
        print(f"ID: {first_processed.get('battle_id')}")
        print(f"Data: {first_processed.get('time')}")
        
        # Verificar detalhes das guilds nesta batalha
        battle_details = first_processed.get('details', {})
        guilds = battle_details.get('guilds', {})
        
        print(f"\nGuilds nesta batalha: {len(guilds)}")
        for guild_name, guild_stats in guilds.items():
            # Verificar se tem marcação de aliança
            is_alliance = guild_stats.get('alliance', False)
            alliance_name = guild_stats.get('alliance_name', '')
            players_count = len(guild_stats.get('players', []))
            player_count_direct = guild_stats.get('player_count', 0)
            
            print(f"\nGuild: {guild_name}")
            print(f"É aliança: {is_alliance}")
            print(f"Nome da aliança: {alliance_name}")
            print(f"Jogadores (lista): {players_count}")
            print(f"Jogadores (contagem direta): {player_count_direct}")
except Exception as e:
    print(f"Erro ao ler o histórico: {e}")