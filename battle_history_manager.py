"""
Módulo para gerenciar o armazenamento e recuperação de histórico de batalhas.
Provê funções para salvar batalhas novas, evitar duplicação e recuperar dados históricos.
"""

import pandas as pd
import json
import os
import logging
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes
HISTORY_FILE = "battle_history.json"  # Arquivo principal de histórico
BACKUP_DIR = "backups"  # Diretório para backups regulares
MAX_HISTORY_DAYS = 90  # Armazenar até 90 dias de histórico

def load_battle_history():
    """
    Carrega o histórico de batalhas do arquivo.
    Retorna um DataFrame vazio se o arquivo não existir.
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history_data = json.load(f)
            
            # Converter para DataFrame
            df = pd.DataFrame(history_data)
            
            # Converter coluna de tempo para datetime
            if not df.empty and 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'])
            
            logging.info(f"Carregado histórico com {len(df)} batalhas")
            return df
        else:
            logging.info("Arquivo de histórico não encontrado. Criando novo histórico.")
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"Erro ao carregar histórico: {e}")
        return pd.DataFrame()

def datetime_converter(obj):
    """
    Conversor personalizado para serializar objetos datetime para JSON
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_battle_history(history_df):
    """
    Salva o histórico de batalhas no arquivo principal.
    Faz um backup se o arquivo já existir.
    """
    try:
        # Garantir que o diretório de backup exista
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            
        # Backup do arquivo atual se existir
        if os.path.exists(HISTORY_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"battle_history_{timestamp}.json")
            
            # Copiar arquivo atual para backup
            with open(HISTORY_FILE, 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            logging.info(f"Backup criado: {backup_file}")
        
        # Criar uma cópia profunda para conversão
        history_data = []
        for _, row in history_df.iterrows():
            # Converter campos problemáticos explicitamente
            battle_record = row.to_dict()
            
            # Converter o campo time para string ISO
            if 'time' in battle_record and isinstance(battle_record['time'], datetime):
                battle_record['time'] = battle_record['time'].isoformat()
                
            # Processar campos aninhados em details
            if 'details' in battle_record and isinstance(battle_record['details'], dict):
                if 'time' in battle_record['details'] and isinstance(battle_record['details']['time'], datetime):
                    battle_record['details']['time'] = battle_record['details']['time'].isoformat()
                    
                # Processar guilds e seus jogadores
                if 'guilds' in battle_record['details']:
                    for guild_name, guild_stats in battle_record['details']['guilds'].items():
                        # Aqui não há campos datetime, mas caso seja adicionado no futuro, 
                        # podemos adicionar conversão adicional
                        pass
            
            history_data.append(battle_record)
        
        # Salvar arquivo principal com conversor personalizado
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history_data, f, default=datetime_converter, indent=2)
        
        logging.info(f"Histórico salvo com {len(history_df)} batalhas")
        
        # Limpar backups antigos
        cleanup_old_backups()
        
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar histórico: {e}")
        return False

def update_battle_history(new_battles_df):
    """
    Atualiza o histórico com novas batalhas, evitando duplicação.
    Retorna o histórico atualizado.
    """
    if new_battles_df.empty:
        logging.info("Nenhuma nova batalha para adicionar ao histórico")
        return load_battle_history()
    
    # Garantir que o DataFrame tem o formato esperado
    required_columns = ['battle_id', 'time', 'players', 'kills', 'deaths', 'fame', 'details']
    for col in required_columns:
        if col not in new_battles_df.columns:
            logging.error(f"Coluna obrigatória ausente nas novas batalhas: {col}")
            return load_battle_history()
    
    # Carregar histórico atual
    history_df = load_battle_history()
    
    # Se não houver histórico, simplesmente usar as novas batalhas
    if history_df.empty:
        logging.info(f"Iniciando novo histórico com {len(new_battles_df)} batalhas")
        save_battle_history(new_battles_df)
        return new_battles_df
    
    # Verificar batalhas duplicadas
    if 'battle_id' in history_df.columns:
        existing_ids = set(history_df['battle_id'].astype(str))
        new_battles_ids = set(new_battles_df['battle_id'].astype(str))
        
        # Filtrar apenas batalhas que não existem no histórico
        unique_battles = new_battles_df[~new_battles_df['battle_id'].astype(str).isin(existing_ids)]
        
        if len(unique_battles) == 0:
            logging.info("Todas as batalhas já existem no histórico")
            return history_df
        
        logging.info(f"Adicionando {len(unique_battles)} novas batalhas ao histórico")
        
        # Combinar histórico com novas batalhas
        updated_df = pd.concat([history_df, unique_battles], ignore_index=True)
        
        # Ordenar por data, mais recentes primeiro
        updated_df = updated_df.sort_values('time', ascending=False).reset_index(drop=True)
        
        # Limitar histórico a MAX_HISTORY_DAYS
        cutoff_date = datetime.now() - timedelta(days=MAX_HISTORY_DAYS)
        updated_df = updated_df[updated_df['time'] >= cutoff_date]
        
        # Salvar histórico atualizado
        save_battle_history(updated_df)
        
        return updated_df
    else:
        # Se o histórico não tiver a coluna battle_id, iniciar novo histórico
        logging.warning("Histórico existente com formato inválido. Criando novo histórico.")
        save_battle_history(new_battles_df)
        return new_battles_df

def get_battles_by_timeframe(days=7):
    """
    Retorna batalhas dentro de um período específico.
    Por padrão, retorna as batalhas dos últimos 7 dias.
    """
    history_df = load_battle_history()
    
    if history_df.empty:
        return pd.DataFrame()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return history_df[history_df['time'] >= cutoff_date].reset_index(drop=True)

def get_daily_stats(days=30):
    """
    Calcula estatísticas diárias a partir do histórico.
    Retorna DataFrame com estatísticas por dia.
    """
    history_df = load_battle_history()
    
    if history_df.empty:
        return pd.DataFrame()
    
    # Filtrar pelo período solicitado
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_df = history_df[history_df['time'] >= cutoff_date]
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    # Criar coluna de data (apenas o dia)
    filtered_df['date'] = filtered_df['time'].dt.date
    
    # Agrupar por dia
    daily_stats = filtered_df.groupby('date').agg({
        'battle_id': 'count',
        'kills': 'sum',
        'deaths': 'sum',
        'fame': 'sum'
    }).reset_index()
    
    # Renomear colunas
    daily_stats.rename(columns={'battle_id': 'battles'}, inplace=True)
    
    # Calcular K/D ratio
    daily_stats['kd_ratio'] = daily_stats['kills'] / daily_stats['deaths'].replace(0, 1)
    
    # Calcular vitórias (kills devem ser 60% maiores que deaths)
    def count_wins(day_battles):
        return sum(day_battles['kills'] >= (day_battles['deaths'] * 1.6))
    
    daily_stats['wins'] = [count_wins(filtered_df[filtered_df['date'] == date]) for date in daily_stats['date']]
    
    # Calcular taxa de vitórias
    daily_stats['win_rate'] = (daily_stats['wins'] / daily_stats['battles']) * 100
    
    # Ordenar por data
    daily_stats = daily_stats.sort_values('date').reset_index(drop=True)
    
    return daily_stats

def cleanup_old_backups(max_backups=10):
    """
    Remove backups antigos, mantendo apenas os mais recentes.
    """
    if not os.path.exists(BACKUP_DIR):
        return
        
    backup_files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) 
                   if f.startswith("battle_history_") and f.endswith(".json")]
    
    if len(backup_files) <= max_backups:
        return
        
    # Ordenar por data de modificação (mais antigos primeiro)
    backup_files.sort(key=lambda f: os.path.getmtime(f))
    
    # Remover os mais antigos
    for f in backup_files[:-max_backups]:
        try:
            os.remove(f)
            logging.info(f"Backup antigo removido: {f}")
        except Exception as e:
            logging.error(f"Erro ao remover backup: {e}")

def print_history_summary():
    """
    Função de diagnóstico para imprimir resumo do histórico.
    """
    history_df = load_battle_history()
    
    if history_df.empty:
        print("Histórico vazio.")
        return
    
    print(f"Histórico contém {len(history_df)} batalhas.")
    print(f"Período: {history_df['time'].min().date()} até {history_df['time'].max().date()}")
    print(f"Total de kills: {history_df['kills'].sum()}")
    print(f"Total de mortes: {history_df['deaths'].sum()}")
    print(f"K/D ratio: {history_df['kills'].sum() / max(1, history_df['deaths'].sum()):.2f}")
    
    # Calcular vitórias
    wins = sum(history_df['kills'] > history_df['deaths'])
    win_rate = (wins / len(history_df)) * 100
    print(f"Vitórias: {wins}/{len(history_df)} ({win_rate:.1f}%)")


if __name__ == "__main__":
    # Testes e diagnóstico
    print_history_summary()