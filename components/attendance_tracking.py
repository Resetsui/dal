
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import format_number

def show_attendance_tracking(battles_df, guild_name):
    st.subheader("📋 Attendance Tracking")
    
    # Extract player attendance data
    players_attendance = {}
    total_battles = len(battles_df)
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        if guild_name in details['guilds']:
            guild_data = details['guilds'][guild_name]
            for player in guild_data['players']:
                name = player['name']
                if name not in players_attendance:
                    players_attendance[name] = {
                        'battles_participated': 0,
                        'attendance_rate': 0
                    }
                players_attendance[name]['battles_participated'] += 1
    
    # Calculate attendance rates
    for player in players_attendance:
        players_attendance[player]['attendance_rate'] = (
            players_attendance[player]['battles_participated'] / total_battles * 100
        )
    
    # Convert to DataFrame for easier manipulation
    attendance_df = pd.DataFrame.from_dict(players_attendance, orient='index')
    attendance_df = attendance_df.sort_values('attendance_rate', ascending=False)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Players", len(players_attendance))
    with col2:
        avg_attendance = attendance_df['attendance_rate'].mean()
        st.metric("Average Attendance Rate", f"{avg_attendance:.1f}%")
    with col3:
        active_players = len(attendance_df[attendance_df['attendance_rate'] > 50])
        st.metric("Active Players (>50%)", active_players)
    
    # Attendance Distribution Chart
    fig = px.bar(
        attendance_df,
        y=attendance_df.index,
        x='attendance_rate',
        orientation='h',
        title='Player Attendance Rates',
        labels={'attendance_rate': 'Attendance Rate (%)', 'index': 'Player'}
    )
    
    fig.update_layout(
        height=max(400, len(players_attendance) * 25),
        showlegend=False,
        xaxis_title="Attendance Rate (%)",
        yaxis_title="Player Name",
        barmode='stack',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed attendance table
    st.subheader("📊 Detailed Attendance")
    
    attendance_df['battles_participated'] = attendance_df['battles_participated'].astype(int)
    attendance_df['attendance_rate'] = attendance_df['attendance_rate'].round(1)
    
    st.dataframe(
        attendance_df.style.format({
            'attendance_rate': '{:.1f}%',
            'battles_participated': '{:.0f}'
        }),
        hide_index=False,
        column_config={
            'battles_participated': 'Battles Participated',
            'attendance_rate': 'Attendance Rate'
        }
    )
