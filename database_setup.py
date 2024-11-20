#River Bumpas & Surya Malik
#CS 2500 Final Project

import sqlite3
import pandas as pd

conn = sqlite3.connect('final_project.db')

game_df = pd.read_csv('game.csv')
player_df = pd.read_csv('common_player_info.csv')
team_df = pd.read_csv('team.csv')

game_df.to_sql('game', conn, if_exists='replace', index=False)
player_df.to_sql('player', conn, if_exists='replace', index=False)
team_df.to_sql('team', conn, if_exists='replace', index=False)

conn.close()