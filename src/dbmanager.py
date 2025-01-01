import sqlite3
import pandas as pd

class StatisticsDatabaseManager:
    def __init__(self, db_path):
        """
        Initializes the database manager and creates the statistics table.

        Args:
            db_path (str): Path to the database file.
        """
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """
        Creates the statistics table in the database if it does not exist.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                player_id TEXT,
                player_name TEXT,
                team_id TEXT,
                team_name TEXT,
                goals INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                ground_duels_won INTEGER,
                ground_duels_won_percentage REAL,
                aerial_duels_won INTEGER,
                aerial_duels_won_percentage REAL,
                successful_dribbles INTEGER,
                successful_dribbles_percentage REAL,
                tackles INTEGER,
                assists INTEGER,
                accurate_passes_percentage REAL,
                total_duels_won INTEGER,
                total_duels_won_percentage REAL,
                minutes_played INTEGER,
                was_fouled INTEGER,
                fouls INTEGER,
                dispossessed INTEGER,
                appearances INTEGER,
                saves INTEGER,
                interceptions INTEGER,
                shots_on_target INTEGER,
                expected_goals REAL,
                PRIMARY KEY (player_id, team_id)
            )
        """)
        self.connection.commit()

    def insert_or_update_statistics(self, dataframe):
        """
        Inserts or updates player statistics in the database.

        Args:
            dataframe (pd.DataFrame): DataFrame containing player statistics.
        """
        for _, row in dataframe.iterrows():
            self.cursor.execute("""
                INSERT INTO statistics (
                    player_id, player_name, team_id, team_name, goals, yellow_cards, red_cards, 
                    ground_duels_won, ground_duels_won_percentage, aerial_duels_won, aerial_duels_won_percentage,
                    successful_dribbles, successful_dribbles_percentage, tackles, assists, 
                    accurate_passes_percentage, total_duels_won, total_duels_won_percentage, minutes_played, 
                    was_fouled, fouls, dispossessed, appearances, saves, interceptions, shots_on_target, expected_goals
                )
                VALUES (
                    :player_id, :player_name, :team_id, :team_name, :goals, :yellow_cards, :red_cards, 
                    :ground_duels_won, :ground_duels_won_percentage, :aerial_duels_won, :aerial_duels_won_percentage,
                    :successful_dribbles, :successful_dribbles_percentage, :tackles, :assists, 
                    :accurate_passes_percentage, :total_duels_won, :total_duels_won_percentage, :minutes_played, 
                    :was_fouled, :fouls, :dispossessed, :appearances, :saves, :interceptions, :shots_on_target, :expected_goals
                )
                ON CONFLICT(player_id, team_id) DO UPDATE SET
                    player_name = excluded.player_name,
                    team_name = excluded.team_name,
                    goals = excluded.goals,
                    yellow_cards = excluded.yellow_cards,
                    red_cards = excluded.red_cards,
                    ground_duels_won = excluded.ground_duels_won,
                    ground_duels_won_percentage = excluded.ground_duels_won_percentage,
                    aerial_duels_won = excluded.aerial_duels_won,
                    aerial_duels_won_percentage = excluded.aerial_duels_won_percentage,
                    successful_dribbles = excluded.successful_dribbles,
                    successful_dribbles_percentage = excluded.successful_dribbles_percentage,
                    tackles = excluded.tackles,
                    assists = excluded.assists,
                    accurate_passes_percentage = excluded.accurate_passes_percentage,
                    total_duels_won = excluded.total_duels_won,
                    total_duels_won_percentage = excluded.total_duels_won_percentage,
                    minutes_played = excluded.minutes_played,
                    was_fouled = excluded.was_fouled,
                    fouls = excluded.fouls,
                    dispossessed = excluded.dispossessed,
                    appearances = excluded.appearances,
                    saves = excluded.saves,
                    interceptions = excluded.interceptions,
                    shots_on_target = excluded.shots_on_target,
                    expected_goals = excluded.expected_goals
            """, {
                'player_id': row['player.id'],
                'player_name': row['player.name'],
                'team_id': row['team.id'],
                'team_name': row['team.name'],
                'goals': row['goals'],
                'yellow_cards': row['yellowCards'],
                'red_cards': row['redCards'],
                'ground_duels_won': row['groundDuelsWon'],
                'ground_duels_won_percentage': row['groundDuelsWonPercentage'],
                'aerial_duels_won': row['aerialDuelsWon'],
                'aerial_duels_won_percentage': row['aerialDuelsWonPercentage'],
                'successful_dribbles': row['successfulDribbles'],
                'successful_dribbles_percentage': row['successfulDribblesPercentage'],
                'tackles': row['tackles'],
                'assists': row['assists'],
                'accurate_passes_percentage': row['accuratePassesPercentage'],
                'total_duels_won': row['totalDuelsWon'],
                'total_duels_won_percentage': row['totalDuelsWonPercentage'],
                'minutes_played': row['minutesPlayed'],
                'was_fouled': row['wasFouled'],
                'fouls': row['fouls'],
                'dispossessed': row['dispossessed'],
                'appearances': row['appearances'],
                'saves': row['saves'],
                'interceptions': row['interceptions'],
                'shots_on_target': row['shotsOnTarget'],
                'expected_goals': row['expectedGoals']
            })
        self.connection.commit()

    def close(self):
        """
        Closes the connection to the database.
        """
        self.connection.close()

