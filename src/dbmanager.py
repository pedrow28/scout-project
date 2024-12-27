import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        """
        Initializes the database manager and creates the necessary tables.

        Args:
            db_path (str): Path to the database file.
        """
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """
        Creates the players and statistics tables in the database.
        """
        # Players Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT,
                team TEXT,
                age INTEGER,
                position TEXT,
                preferred_foot TEXT
            )
        """)

        # Statistics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                player_id TEXT,
                stat TEXT,
                per_90_minutes REAL,
                percentile REAL,
                PRIMARY KEY (player_id, stat),
                FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE ON UPDATE NO ACTION
            )
        """)

        self.connection.commit()

    def insert_or_update_players(self, players):
        """
        Inserts or updates player information in the database.

        Args:
            players (list of dict): Player data, including id, name, team, age, position, and preferred_foot.
        """
        for player in players:
            self.cursor.execute("""
                INSERT INTO players (player_id, name, team, age, position, preferred_foot)
                VALUES (:player_id, :name, :team, :age, :position, :preferred_foot)
                ON CONFLICT(player_id) DO UPDATE SET
                    name = excluded.name,
                    team = excluded.team,
                    age = excluded.age,
                    position = excluded.position,
                    preferred_foot = excluded.preferred_foot
            """, {
                'player_id': player['player_id'],
                'name': player['name'],
                'team': player['team'],
                'age': player['age'],
                'position': player['position'],
                'preferred_foot': player['foot']
            })
        self.connection.commit()

    def insert_or_update_statistics(self, statistics):
        """
        Inserts or updates player statistics in the database.

        Args:
            statistics (list of dict): List of player statistics.
        """
        for stat in statistics:
            self.cursor.execute("""
                INSERT INTO statistics (player_id, stat, per_90_minutes, percentile)
                VALUES (:player_id, :stat, :per_90_minutes, :percentile)
                ON CONFLICT(player_id, stat) DO UPDATE SET
                    per_90_minutes = excluded.per_90_minutes,
                    percentile = excluded.percentile
            """, {
                'player_id': stat['player_id'],  # Matches 'jogador_id' from the statistics field
                'stat': stat['stat'],  # Matches 'stat'
                'per_90_minutes': stat['per_90_minutes'],  # Matches 'per_90_minutes'
                'percentile': stat['percentil']  # Matches 'percentil'
            })
        self.connection.commit()

    def close(self):
        """
        Closes the connection to the database.
        """
        self.connection.close()
