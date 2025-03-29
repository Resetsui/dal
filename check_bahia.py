import json

# Carregar os dados brutos
with open('data.json', 'r') as f:
    battles = json.load(f)

print('Verificando guilds da aliança BAHIA...')

# Verificar as primeiras batalhas
for i, battle in enumerate(battles[:5]):
    print(f'\nBatalha {i+1} (ID: {battle.get("id")}):')
    
    # Encontrar jogadores da aliança BAHIA
    bahia_players = [
        p for p_id, p in battle.get('players', {}).items() 
        if p.get('allianceName') == 'BAHlA'
    ]
    
    print(f'Jogadores da aliança BAHIA: {len(bahia_players)}')
    
    if bahia_players:
        # Contar jogadores por guild
        guild_counts = {}
        for p in bahia_players:
            guild_name = p.get('guildName', 'Unknown')
            if guild_name not in guild_counts:
                guild_counts[guild_name] = 0
            guild_counts[guild_name] += 1
        
        print('Guilds da aliança BAHlA:')
        for guild, count in guild_counts.items():
            print(f' - {guild}: {count} jogadores')

# Agora verificar o histórico de batalhas processadas
print("\n\nVerificando histórico processado...")
try:
    with open('battle_history.json', 'r') as f:
        history = json.load(f)
    
    for i, battle in enumerate(history[:5]):
        print(f'\nBatalha processada {i+1} (ID: {battle.get("battle_id")}):')
        
        # Verificar as guilds nos detalhes
        guilds_data = battle.get('details', {}).get('guilds', {})
        
        # Mostrar informações de todas as guilds
        for guild_name, guild_stats in guilds_data.items():
            is_alliance = guild_stats.get('alliance', False)
            alliance_name = guild_stats.get('alliance_name', '')
            
            # Contar jogadores
            players_count = len(guild_stats.get('players', []))
            player_count = guild_stats.get('player_count', 0)
            
            # Se for aliança ou tiver nome de aliança, mostrar detalhes
            if is_alliance or 'alliance_name' in guild_stats:
                print(f' - Guild: {guild_name}')
                print(f'   Marcada como aliança: {is_alliance}')
                print(f'   Nome da aliança: {alliance_name}')
                print(f'   Jogadores: {players_count if not player_count else player_count}')
except Exception as e:
    print(f"Erro ao ler o histórico: {e}")