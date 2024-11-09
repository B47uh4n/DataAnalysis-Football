import customtkinter as ctk
import pandas as pd
import requests
from pandas import json_normalize
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
import numpy as np

# en alttaki 3 buton tum takim istatistiklerini gosteriyor bu daha sonra uygulamanin son halinde bir feature olarak eklenir.
# mac datalarini visualize etmek icin statsbomb tercih ettim  https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/3906390.json
events = requests.get('https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/3775635.json').json()
df = json_normalize(events)

# unique teams from the data
team_names = df['team.name'].unique()

# ctk window initialize ettim
app = ctk.CTk()
app.title("Football Data Analysis")
app.geometry("500x550")

# variables to store selections
half_var = ctk.StringVar()
team1_var = ctk.StringVar()
team2_var = ctk.StringVar()
player_var = ctk.StringVar()

# Half selection combo box
#get_data_by_half(df) gibi bir fonk icinde skorlar alip en uste mac skoru yazabiliriz.
#ctk.CTkLabel(app, text="Score:").pack(pady=30)
ctk.CTkLabel(app, text="Select Half:").pack(pady=10)
half_combo = ctk.CTkComboBox(app, values=["First Half", "Second Half", "Full Match"], variable=half_var)
half_combo.pack(pady=10)

# Team selection combo boxes
ctk.CTkLabel(app, text="Select Team 1:").pack(pady=10)
team1_combo = ctk.CTkComboBox(app, values=team_names, variable=team1_var)
team1_combo.pack(pady=10)

ctk.CTkLabel(app, text="Select Team 2 (Optional):").pack(pady=10)
team2_combo = ctk.CTkComboBox(app, values=team_names, variable=team2_var)
team2_combo.pack(pady=10)

# Player selection combo box
ctk.CTkLabel(app, text="Select Player (Optional):").pack(pady=10)
player_combo = ctk.CTkComboBox(app, values=[], variable=player_var)
player_combo.pack(pady=10)

# Fetch players with positions
def get_players_for_team(selected_team):
    players = df[df['team.name'] == selected_team][['player.name', 'position.name']].dropna()
    return [f"{row['player.name']}, {row['position.name']}" for idx, row in players.iterrows()]

# Oyuncu listesi güncellemesi yapılırken tekrar edenleri önlemek için bosalttim
def update_player_list(*args):
    player_combo.set("")  # Oyuncu secimini sifirla
    selected_team = team1_var.get() or team2_var.get()  # Secilen takimi al
    if selected_team:
        players = get_players_for_team(selected_team)
        player_combo.configure(values=list(set(players)))  # Tekrarlanan oyunculari kaldir

team1_var.trace_add('write', update_player_list)
team2_var.trace_add('write', update_player_list)

# Veri görselleme fonksiyonlarını sadece seçilen oyuncuya göre filtrelemek için düzenledim
# selected half icin datalari fetchledim
def get_data_by_half(data):
    selected_half = half_var.get()
    if selected_half == "First Half":
        return data[data['period'] == 1]
    elif selected_half == "Second Half":
        return data[data['period'] == 2]
    else:  # Full Match
        return data

# Modify the apply_selection_for_player function to work with filtered data
def apply_selection_for_player(data):
    data = get_data_by_half(data)  # Filter by half
    player = player_var.get().split(",")[0] if player_var.get() else None  # Get the selected player
    if player:
        return data[data['player.name'] == player]  # Filter by selected player
    return data

# Update the visualization functions
def plot_passes(data):
    filtered_data = apply_selection_for_player(data)
    fig, ax = plt.subplots(figsize=(15.6, 10.4))
    fig.set_facecolor('black')
    ax.patch.set_facecolor('black')
    
    pitch = Pitch(pitch_type='statsbomb', positional=True, positional_color='#9A9A9A',
                  pitch_color='grass', line_color='#c7d5cc', goal_type='box')
    pitch.draw(ax=ax)
    
    passes = filtered_data[filtered_data['type.name'] == 'Pass']
    x = passes['location'].apply(lambda loc: loc[0] if loc else np.nan)
    y = passes['location'].apply(lambda loc: loc[1] if loc else np.nan)
    ax.scatter(x, y, color='blue', alpha=0.6)
    plt.title("Passes Visualization")
    plt.show()

# Similarly update plot_passes_origin and plot_shots_goals using get_data_by_half

# plot_passes_origin
def plot_passes_origin(data):
    filtered_data = apply_selection_for_player(data)
    fig, ax = plt.subplots(figsize=(15.6, 10.4))
    fig.set_facecolor('black')
    ax.patch.set_facecolor('black')
    
    pitch = Pitch(pitch_type='statsbomb', positional=True, positional_color='#9A9A9A',
                  pitch_color='grass', line_color='#c7d5cc', goal_type='box')
    pitch.draw(ax=ax)
    
    passes = filtered_data[filtered_data['type.name'] == 'Pass']
    x = passes['location'].apply(lambda loc: loc[0] if loc else np.nan)
    y = passes['location'].apply(lambda loc: loc[1] if loc else np.nan)
    x_end = passes['pass.end_location'].apply(lambda loc: loc[0] if loc else np.nan)
    y_end = passes['pass.end_location'].apply(lambda loc: loc[1] if loc else np.nan)
    
    ax.scatter(x, y, color='blue', label="Start", alpha=0.6)
    ax.scatter(x_end, y_end, color='red', label="End", alpha=0.6)
    
    for i in range(len(passes)):
        ax.arrow(x.iloc[i], y.iloc[i], x_end.iloc[i] - x.iloc[i], y_end.iloc[i] - y.iloc[i],
                 head_width=1, color='green', alpha=0.5)
    
    plt.title("Passes Origin to Destination")
    plt.legend()
    plt.show()

# Buttons remain the same but now visualize filtered data based on half


def plot_shots_goals(data):
    filtered_data = apply_selection_for_player(data)
    pitch = Pitch()
    fig, ax = plt.subplots(figsize=(10, 6))
    pitch.draw(ax=ax)
    
    shots = filtered_data[filtered_data['type.name'] == 'Shot']
    x_shot = shots['location'].apply(lambda loc: loc[0] if loc else np.nan)
    y_shot = shots['location'].apply(lambda loc: loc[1] if loc else np.nan)
    goals = shots[shots['shot.outcome.name'] == 'Goal']
    x_goals = goals['location'].apply(lambda loc: loc[0] if loc else np.nan)
    y_goals = goals['location'].apply(lambda loc: loc[1] if loc else np.nan)
    
    ax.scatter(x_shot, y_shot, color='blue', label="Shots", alpha=0.6)
    ax.scatter(x_goals, y_goals, color='red', label="Goals", alpha=0.8)
    
    plt.title("Shots and Goals")
    plt.legend()
    plt.show()

# Butonların her birini seçilen oyuncu verileriyle ilişkilendirme
passes_button = ctk.CTkButton(app, text="Visualize Passes", command=lambda: plot_passes(df))
passes_button.pack(pady=10)

passes_origin_button = ctk.CTkButton(app, text="Visualize Passes Origin", command=lambda: plot_passes_origin(df))
passes_origin_button.pack(pady=10)

shots_goals_button = ctk.CTkButton(app, text="Visualize Shots and Goals", command=lambda: plot_shots_goals(df))
shots_goals_button.pack(pady=10)

app.mainloop()
