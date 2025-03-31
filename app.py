import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import time
from datetime import datetime

# Importação corrigida
from direct_scraper import get_battle_data

# Configuração da página Streamlit
st.set_page_config(
    page_title="Battle Data Analyzer",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para exibir os dados de batalha
def display_battle_data():
    st.header("Dados de Batalha")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.text_input("ID do Usuário (opcional)")
    
    with col2:
        battle_id = st.text_input("ID da Batalha (opcional)")
    
    if st.button("Buscar Dados de Batalha"):
        with st.spinner("Buscando dados..."):
            data = get_battle_data(
                user_id=user_id if user_id else None, 
                battle_id=battle_id if battle_id else None
            )
            
            if "error" in data:
                st.error(data["error"])
            else:
                st.success("Dados encontrados!")
                
                # Exibir dados em formato JSON
                with st.expander("Ver JSON completo", expanded=False):
                    st.json(data)
                
                # Exibir dados em formato tabular se for uma lista
                if isinstance(data, list) and len(data) > 0:
                    st.subheader("Resumo das Batalhas")
                    
                    # Criar DataFrame para exibição
                    battle_df = pd.DataFrame(data)
                    st.dataframe(battle_df)
                    
                    # Mostrar algumas estatísticas
                    if "result" in battle_df.columns:
                        st.subheader("Estatísticas")
                        results = battle_df["result"].value_counts()
                        st.bar_chart(results)
                
                # Exibir detalhes de uma única batalha
                elif isinstance(data, dict) and "id" in data:
                    st.subheader(f"Detalhes da Batalha: {data['id']}")
                    
                    # Exibir informações em colunas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Data:**", data.get("date", "N/A"))
                        st.write("**Resultado:**", data.get("result", "N/A"))
                        st.write("**Tipo:**", data.get("type", "N/A"))
                    
                    with col2:
                        st.write("**Jogador:**", data.get("player_name", "N/A"))
                        st.write("**Oponente:**", data.get("opponent_name", "N/A"))
                        st.write("**Pontuação:**", data.get("score", "N/A"))

# Função para exibir estatísticas gerais
def display_statistics():
    st.header("Estatísticas Gerais")
    
    # Carregar todos os dados de batalha
    all_data = get_battle_data()
    
    if "error" in all_data:
        st.error(all_data["error"])
        return
    
    if not isinstance(all_data, list) or len(all_data) == 0:
        st.warning("Não há dados suficientes para gerar estatísticas.")
        return
    
    # Criar DataFrame
    df = pd.DataFrame(all_data)
    
    # Exibir contagem total
    st.metric("Total de Batalhas", len(df))
    
    # Exibir estatísticas em colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "result" in df.columns:
            st.subheader("Resultados")
            results = df["result"].value_counts()
            st.bar_chart(results)
    
    with col2:
        if "type" in df.columns:
            st.subheader("Tipos de Batalha")
            types = df["type"].value_counts()
            st.bar_chart(types)
    
    with col3:
        if "date" in df.columns:
            st.subheader("Batalhas por Período")
            # Converter para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(df["date"]):
                df["date"] = pd.to_datetime(df["date"])
            
            # Agrupar por mês
            df["month"] = df["date"].dt.strftime("%Y-%m")
            monthly = df.groupby("month").size()
            st.bar_chart(monthly)

# Função principal
def main():
    st.title("⚔️ Analisador de Dados de Batalha")
    
    # Barra lateral
    st.sidebar.title("Navegação")
    page = st.sidebar.radio(
        "Selecione uma página:",
        ["Dados de Batalha", "Estatísticas", "Sobre"]
    )
    
    # Exibir página selecionada
    if page == "Dados de Batalha":
        display_battle_data()
    elif page == "Estatísticas":
        display_statistics()
    else:
        st.header("Sobre")
        st.write("""
        ## Analisador de Dados de Batalha
        
        Esta aplicação permite visualizar e analisar dados de batalhas.
        
        ### Funcionalidades:
        - Busca de batalhas por ID de usuário ou ID de batalha
        - Visualização detalhada de batalhas individuais
        - Estatísticas gerais sobre todas as batalhas
        
        ### Tecnologias utilizadas:
        - Python
        - Streamlit
        - Pandas
        - NumPy
        """)
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.info("Desenvolvido com ❤️ usando Streamlit")

if __name__ == "__main__":
    main()
