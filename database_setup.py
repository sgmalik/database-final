#River Bumpas & Surya Malik
#CS 2500 Final Project

import sqlite3
import pandas as pd

conn = sqlite3.connect('final_project.db')

# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON;")

# Create the tables
conn.execute("""
CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    nickname TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    year_founded REAL NOT NULL
);
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS player (
    person_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    display_first_last TEXT,
    birthdate TEXT,
    school TEXT,
    country TEXT,
    last_affiliation TEXT,
    height TEXT,
    weight REAL,
    season_exp REAL,
    jersey TEXT,
    position TEXT,
    rosterstatus TEXT,
    team_id INTEGER,
    team_name TEXT,
    team_abbreviation TEXT,
    team_city TEXT,
    from_year REAL,
    to_year REAL,
    nba_flag TEXT,
    games_played_flag TEXT,
    draft_year TEXT,
    draft_round TEXT,
    draft_number TEXT,
    greatest_75_flag TEXT,
    FOREIGN KEY (team_id) REFERENCES team(id)
);
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS game (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER,
    team_id_home INTEGER,
    team_name_home TEXT,
    team_abbreviation_home TEXT,
    game_id INTEGER,
    game_date TEXT,
    matchup_home TEXT,
    wl_home TEXT,
    min INTEGER,
    fgm_home REAL,
    fga_home REAL,
    fg_pct_home REAL,
    fg3m_home REAL,
    fg3a_home REAL,
    fg3_pct_home REAL,
    ftm_home REAL,
    fta_home REAL,
    ft_pct_home REAL,
    oreb_home REAL,
    dreb_home REAL,
    reb_home REAL,
    ast_home REAL,
    stl_home REAL,
    blk_home REAL,
    tov_home REAL,
    pf_home REAL,
    pts_home REAL,
    plus_minus_home INTEGER,
    team_id_away INTEGER,
    team_name_away TEXT,
    team_abbreviation_away TEXT,
    matchup_away TEXT,
    wl_away TEXT,
    fgm_away REAL,
    fga_away REAL,
    fg_pct_away REAL,
    fg3m_away REAL,
    fg3a_away REAL,
    fg3_pct_away REAL,
    ftm_away REAL,
    fta_away REAL,
    ft_pct_away REAL,
    oreb_away REAL,
    dreb_away REAL,
    reb_away REAL,
    ast_away REAL,
    stl_away REAL,
    blk_away REAL,
    tov_away REAL,
    pf_away REAL,
    pts_away REAL,
    plus_minus_away INTEGER,
    FOREIGN KEY (team_id_home) REFERENCES team(id),
    FOREIGN KEY (team_id_away) REFERENCES team(id)
);
""")

# Populate tables with data from CSV files
game_df = pd.read_csv('game.csv').drop('video_available_home', axis=1).drop('video_available_away', axis=1).drop('season_type', axis=1)
player_df = pd.read_csv('common_player_info.csv').drop('display_last_comma_first', axis=1).drop('display_fi_last', axis=1).drop('player_slug', axis=1).drop('games_played_current_season_flag', axis=1).drop('team_code', axis=1).drop('playercode', axis=1).drop('dleague_flag', axis=1)
team_df = pd.read_csv('team.csv')

# Filter out invalid `team_id` values in `player` and `game`
valid_team_ids = set(team_df['id'])

# Drop rows in `player` with invalid `team_id`
player_df = player_df[player_df['team_id'].isin(valid_team_ids)]

# Drop rows in `game` with invalid `team_id_home` or `team_id_away`
game_df = game_df[game_df['team_id_home'].isin(valid_team_ids) & game_df['team_id_away'].isin(valid_team_ids)]

team_df.to_sql('team', conn, if_exists='append', index=False)
player_df.to_sql('player', conn, if_exists='append', index=False)
game_df.to_sql('game', conn, if_exists='append', index=False)

conn.close()