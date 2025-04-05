import os
import sqlite3
from datetime import datetime, timedelta
import zoneinfo


def execute_db_command(command: str, parameters: tuple = (), get=False) -> list | None:
    """
    Execute command to DB
    """
    retval = None
    with sqlite3.connect(os.getenv("DB_NAME")) as db:
        cursor = db.cursor()
        cursor.execute(
            command,
            parameters,
        )
        if get:
            retval = cursor.fetchall()
        return retval


def initialize_db():
    """Create the database and tables if they don't exist."""
    # Wordle. Added hard_mode column and made skill/luck nullable
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS wordle_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            game_number TEXT,
            attempts INTEGER,
            skill INTEGER NULL,
            luck INTEGER NULL,
            hard_mode BOOLEAN,
            total_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Connections table (corrected)
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS connections_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            puzzle_number TEXT,
            total_score INTEGER,
            guesses INTEGER,
            solved_purple_first BOOLEAN,
            solved_blue_first BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # New generic table for tracking latest game numbers
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS latest_game_numbers (
            game_name TEXT PRIMARY KEY,
            latest_number INTEGER
        )
        """
    )

    # Initialize with 0 if empty
    # TODO: remove this hardcode here
    for game in ["wordle", "connections", "framed", "gisnep", "bandle"]:
        execute_db_command(
            "INSERT OR IGNORE INTO latest_game_numbers (game_name, latest_number) VALUES (?, 0)",
            (game,),
        )

    # Framed Table
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS framed_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            game_number INTEGER,
            attempts INTEGER,
            total_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Gisnep Table (Stores time instead of points)
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS gisnep_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            game_number INTEGER,
            completion_time INTEGER, -- Time in seconds
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Bandle Table
    execute_db_command(
        """
        CREATE TABLE IF NOT EXISTS bandle_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT,
            game_number INTEGER,
            attempts INTEGER,
            total_score INTEGER,
            bonus_completed INTEGER,
            bonus_total INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def save_wordle_score(
    user_id, display_name, game_number, attempts, skill=None, luck=None, hard_mode=False
):
    """Save a new Wordle score with optional skill, luck, and hard mode flag."""
    score = 100 - ((attempts - 1) * 20)
    if score < 0:
        score = 0

    total_score = (skill or 0) + score - (luck or 0)

    execute_db_command(
        """
            INSERT INTO wordle_scores (user_id, display_name, game_number, attempts, skill, luck, hard_mode, total_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (
            user_id,
            display_name,
            game_number,
            attempts,
            skill,
            luck,
            hard_mode,
            total_score,
        ),
    )


def save_connections_score(
    user_id,
    display_name,
    puzzle_number,
    total_score,
    guesses,
    solved_purple_first,
    solved_blue_first,
):
    """Save a new Connections score."""
    execute_db_command(
        """
            INSERT INTO connections_scores (user_id, display_name, puzzle_number, total_score, guesses, solved_purple_first, solved_blue_first)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            display_name,
            puzzle_number,
            total_score,
            guesses,
            solved_purple_first,
            solved_blue_first,
        ),
    )


def create_connections_scores_table():
    """Create the Connections scores table if it doesn't exist."""
    execute_db_command(
        """
            CREATE TABLE IF NOT EXISTS connections_scores (
                user_id INTEGER,
                display_name TEXT,
                puzzle_number INTEGER,
                total_score INTEGER,
                guesses INTEGER,
                solved_purple_first BOOLEAN,
                solved_blue_first BOOLEAN,
                PRIMARY KEY (user_id, puzzle_number)
            )
        """
    )


def save_framed_score(user_id, display_name, game_number, attempts, total_score):
    """Save a new Framed score."""
    execute_db_command(
        """
            INSERT INTO framed_scores (user_id, display_name, game_number, attempts, total_score)
            VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, display_name, game_number, attempts, total_score),
    )


def save_gisnep_score(user_id, display_name, game_number, completion_time):
    """Save a new Gisnep score (only stores time)."""
    execute_db_command(
        """
        INSERT INTO gisnep_scores (user_id, display_name, game_number, completion_time)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, display_name, game_number, completion_time),
    )


def save_bandle_score(
    user_id,
    display_name,
    game_number,
    attempts,
    total_score,
    bonus_completed,
    bonus_total,
):
    """Save a new Bandle score, including bonus rounds separately."""
    execute_db_command(
        """
            INSERT INTO bandle_scores (user_id, display_name, game_number, attempts, total_score, bonus_completed, bonus_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            display_name,
            game_number,
            attempts,
            total_score,
            bonus_completed,
            bonus_total,
        ),
    )


# Database functions for tracking roles (add these to your database.py file)
def save_user_role(user_id, role_name, game_number, expires_at):
    """Save information about a role granted to a user."""
    execute_db_command(
        """
        INSERT OR REPLACE INTO user_roles 
        (user_id, role_name, game_number, expires_at) 
        VALUES (?, ?, ?, ?)
        """,
        (user_id, role_name, game_number, expires_at),
    )


def get_recent_scores(user_id, limit=5) -> list:
    """Retrieve the last `limit` games played by a user."""
    return execute_db_command(
        """
                SELECT game_number, attempts, skill, luck, timestamp
                FROM wordle_scores
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
        (user_id, limit),
        True,
    )


def get_wordle_leaderboard() -> list:
    """Fetch the top players for Wordle leaderboard."""
    return execute_db_command(
        """
                SELECT display_name, MAX(total_score) AS best_score
                FROM wordle_scores
                GROUP BY display_name
                ORDER BY best_score DESC
                LIMIT 10
            """,
        get=True,
    )


def get_connections_leaderboard():
    """Fetch the top players for Connections leaderboard."""
    return execute_db_command(
        """
                SELECT display_name, SUM(total_score) AS total_score
                FROM connections_scores
                GROUP BY display_name
                ORDER BY total_score DESC
                LIMIT 10
            """,
        get=True,
    )


def get_framed_leaderboard():
    """Fetch top players for Framed based on highest scores."""
    return execute_db_command(
        """
            SELECT display_name, MAX(total_score) AS best_score
            FROM framed_scores
            GROUP BY display_name
            ORDER BY best_score DESC
            LIMIT 10
            """,
        get=True,
    )


def get_gisnep_leaderboard():
    """Fetch top players for Gisnep, ranking by shortest average time."""
    return execute_db_command(
        """
            SELECT display_name, AVG(completion_time) AS avg_time, COUNT(*) AS games_played
            FROM gisnep_scores
            GROUP BY display_name
            ORDER BY avg_time ASC, games_played DESC
            LIMIT 10
            """,
        get=True,
    )


def get_bandle_leaderboard():
    """Fetch top players for Bandle based on highest total scores."""
    return execute_db_command(
        """
        SELECT display_name, SUM(total_score) AS total_score
        FROM bandle_scores
        GROUP BY display_name
        ORDER BY total_score DESC
        LIMIT 10
        """
    )


def get_weekly_scores():
    """Fetch total scores for all games for the past week."""
    # Todo, set default one place
    one_week_ago = (
        datetime.now(zoneinfo.ZoneInfo(os.getenv("TIMEZONE", "Europe/Berlin")))
        - timedelta(days=7)
    ).strftime("%Y-%m-%d %H:%M:%S")
    wordle = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM wordle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (one_week_ago,),
        get=True,
    )
    connections = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM connections_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (one_week_ago,),
        get=True,
    )
    framed = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM framed_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (one_week_ago,),
        get=True,
    )
    gisnep = execute_db_command(
        """
            SELECT display_name, AVG(completion_time) AS avg_time
            FROM gisnep_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY avg_time ASC
        """,
        (one_week_ago,),
        get=True,
    )
    bandle = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM bandle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (one_week_ago,),
        get=True,
    )
    return {
        "Wordle": wordle,
        "Connections": connections,
        "Framed": framed,
        "Gisnep": gisnep,
        "Bandle": bandle,
    }


def get_monthly_scores():
    """Fetch total scores for all games for the past month."""

    first_day_of_month = (
        datetime.now(zoneinfo.ZoneInfo(os.getenv("TIMEZONE", "Europe/Berlin")))
        .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )
    wordle = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM wordle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (first_day_of_month,),
        get=True,
    )
    connections = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM connections_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (first_day_of_month,),
        get=True,
    )
    framed = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM framed_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (first_day_of_month,),
        get=True,
    )
    gisnep = execute_db_command(
        """
            SELECT display_name, AVG(completion_time) AS avg_time
            FROM gisnep_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY avg_time ASC
        """,
        (first_day_of_month,),
        get=True,
    )
    bandle = execute_db_command(
        """
            SELECT display_name, SUM(total_score) AS total_score
            FROM bandle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
        (first_day_of_month,),
        get=True,
    )
    return {
        "Wordle": wordle,
        "Connections": connections,
        "Framed": framed,
        "Gisnep": gisnep,
        "Bandle": bandle,
    }


def get_expired_roles():
    """Get all expired roles that need to be removed."""
    now = datetime.datetime.now(
        zoneinfo.ZoneInfo(os.getenv("TIMEZONE", "Europe/Berlin"))
    ).strftime("%Y-%m-%d %H:%M:%S")
    return execute_db_command(
        """
        SELECT user_id, role_name FROM user_roles
        WHERE expires_at < ?
        """,
        (now,),
        get=True,
    )


def delete_expired_roles():
    """Delete records of expired roles from the database."""
    now = datetime.datetime.now(
        zoneinfo.ZoneInfo(os.getenv("TIMEZONE", "Europe/Berlin"))
    ).strftime("%Y-%m-%d %H:%M:%S")
    execute_db_command(
        """
        DELETE FROM user_roles WHERE expires_at < ?
        """,
        (now,),
    )


def get_overall_recent_wordle_scores(limit=5):
    """
    Fetches the most recent Wordle scores from all users, ordered by timestamp descending,
    limited to the specified number.
    """
    return execute_db_command(
        """
            SELECT game_number, attempts, skill, luck, timestamp
            FROM wordle_scores
            ORDER BY timestamp DESC
            LIMIT ?
        """,
        (limit,),
        get=True,
    )


def get_overall_recent_connections_puzzle_number(limit=5):
    """
    Fetches the most recent Connections puzzle numbers from all users,
    ordered by timestamp descending, limited to the specified number.
    Returns a list of tuples, each containing (puzzle_number, timestamp).
    """
    return execute_db_command(
        """
            SELECT puzzle_number, timestamp
            FROM connections_scores
            ORDER BY timestamp DESC
            LIMIT ?
        """,
        (limit,),
        get=True,
    )


def get_latest_game_number_from_db(game_name):
    """Fetches the latest game number from the database."""
    numbers = execute_db_command(
        "SELECT latest_number FROM latest_game_numbers WHERE game_name = ?",
        (game_name,),
        get=True,
    )
    if numbers:
        print(
            f"DB: Retrieved latest_number for {game_name} = {numbers[-1]}"
        )  # DEBUGGING
        return numbers[-1]
    else:
        return 0


def update_latest_game_number_in_db(game_name, latest_number):
    """Updates the latest game number in the database."""
    execute_db_command(
        "INSERT OR REPLACE INTO latest_game_numbers (game_name, latest_number) VALUES (?, ?)",
        (
            game_name,
            latest_number,
        ),
    )
    print(f"DB: Updated latest_number for {game_name} to {latest_number}")  # DEBUGGING
