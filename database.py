import os
import sqlite3
from datetime import datetime, timedelta
from game_config import GAME_CONFIGS


def initialize_db():
    """Create the database and tables if they don't exist."""
    try:
        with sqlite3.connect(os.getenv("DB_NAME")) as db:
            cursor = db.cursor()
            # Wordle. Added hard_mode column and made skill/luck nullable
            cursor.execute(
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
            cursor.execute(
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
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS latest_game_numbers (
                    game_name TEXT PRIMARY KEY,
                    latest_number INTEGER
                )
            """
            )

            # Initialize with 0 if empty
            for game in GAME_CONFIGS.keys():
                cursor.execute(
                    "INSERT OR IGNORE INTO latest_game_numbers (game_name, latest_number) VALUES (?, 0)",
                    (game,),
                )

            # Framed Table
            cursor.execute(
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
            cursor.execute(
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
            cursor.execute(
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
    except sqlite3.Error as e:
        print(f"Failed to initialize db: {e}")
        exit(1)


def execute_db_command(command: str, parameters: tuple = (), get=False) -> list | None:
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


def save_wordle_score(
    user_id, display_name, game_number, attempts, skill=None, luck=None, hard_mode=False
):
    """Save a new Wordle score with optional skill, luck, and hard mode flag."""
    score = 100 - ((attempts - 1) * 20)
    if score < 0:
        score = 0

    total_score = (skill or 0) + score - (luck or 0)
    try:
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
    except sqlite3.Error as e:
        print(
            f"Could not save Wordle score for {user_id}/{display_name}/{game_number}: {e}"
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
    try:
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
    except sqlite3.Error as e:
        print(
            f"Could not save new connections score for {user_id}/{display_name}/{puzzle_number}: {e}"
        )


def create_connections_scores_table():
    """Create the Connections scores table if it doesn't exist."""
    try:
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
    except sqlite3.Error as e:
        print(f"Could not create connections score table: {e}")


def save_framed_score(user_id, display_name, game_number, attempts, total_score):
    """Save a new Framed score."""
    try:
        execute_db_command(
            """
                INSERT INTO framed_scores (user_id, display_name, game_number, attempts, total_score)
                VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, display_name, game_number, attempts, total_score),
        )
    except sqlite3.Error as e:
        print(f"Could not save new Framed score: {e}")


def save_gisnep_score(user_id, display_name, game_number, completion_time):
    """Save a new Gisnep score (only stores time)."""
    try:
        execute_db_command(
            """
            INSERT INTO gisnep_scores (user_id, display_name, game_number, completion_time)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, display_name, game_number, completion_time),
        )
    except sqlite3.Error as e:
        print(
            f"Could not save new Gisnep score for {user_id}/{display_name}/{game_number}: {e}"
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
    try:
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
    except sqlite3.Error as e:
        print(
            f"Could not save a new Bandle score for {user_id}/{display_name}/{game_number}: {e}"
        )


def get_recent_scores(user_id, limit=5) -> list | None:
    """Retrieve the last `limit` games played by a user."""
    retval = None
    try:
        retval = execute_db_command(
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
    except sqlite3.Error as e:
        print(f"Could not retrieve last 'limit' games played by {user_id}: {e}")
    finally:
        return retval


def get_wordle_leaderboard() -> list:
    """Fetch the top players for Wordle leaderboard."""
    leaderboard = []
    try:
        leaderboard = execute_db_command(
            """
                SELECT display_name, MAX(total_score) AS best_score
                FROM wordle_scores
                GROUP BY display_name
                ORDER BY best_score DESC
                LIMIT 10
            """,
            get=True,
        )
    except sqlite3.Error as e:
        print(f"Could not fetch top players for wordle leaderboard: {e}")
    finally:
        return leaderboard


def get_connections_leaderboard():
    """Fetch the top players for Connections leaderboard."""
    leaderboard = []
    try:
        leaderboard = execute_db_command(
            """
                SELECT display_name, SUM(total_score) AS total_score
                FROM connections_scores
                GROUP BY display_name
                ORDER BY total_score DESC
                LIMIT 10
            """,
            get=True,
        )
    except sqlite3.Error as e:
        print(f"Could not fetch top players for connections leaderboard: {e}")
    finally:
        return leaderboard


def get_framed_leaderboard():
    """Fetch top players for Framed based on highest scores."""
    leaderboard = []
    try:
        leaderboard = execute_db_command(
            """
            SELECT display_name, MAX(total_score) AS best_score
            FROM framed_scores
            GROUP BY display_name
            ORDER BY best_score DESC
            LIMIT 10
            """,
            get=True,
        )
    except sqlite3.Error as e:
        print(f"Could not fetch top players for framed: {e}")
    finally:
        return []


def get_gisnep_leaderboard():
    """Fetch top players for Gisnep, ranking by shortest average time."""
    leaderboard = []
    try:
        leaderboard = execute_db_command(
            """
            SELECT display_name, AVG(completion_time) AS avg_time, COUNT(*) AS games_played
            FROM gisnep_scores
            GROUP BY display_name
            ORDER BY avg_time ASC, games_played DESC
            LIMIT 10
            """,
            get=True,
        )
    except sqlite3.Error as e:
        print(f"Could not fetch top players for gisnep: {e}")
    finally:
        return leaderboard


def get_bandle_leaderboard():
    """Fetch top players for Bandle based on highest total scores."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT display_name, SUM(total_score) AS total_score
        FROM bandle_scores
        GROUP BY display_name
        ORDER BY total_score DESC
        LIMIT 10
    """
    )
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard


def get_weekly_scores():
    """Fetch total scores for all games for the past week."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Wordle
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM wordle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (one_week_ago,),
        )
        wordle_scores = cursor.fetchall()

        # Connections
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM connections_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (one_week_ago,),
        )
        connections_scores = cursor.fetchall()

        # Framed
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM framed_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (one_week_ago,),
        )
        framed_scores = cursor.fetchall()

        # Gisnep (rank by shortest average time)
        cursor.execute(
            """
            SELECT display_name, AVG(completion_time) AS avg_time
            FROM gisnep_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY avg_time ASC
        """,
            (one_week_ago,),
        )
        gisnep_scores = cursor.fetchall()

        # Bandle
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM bandle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (one_week_ago,),
        )
        bandle_scores = cursor.fetchall()

        conn.close()

        return {
            "Wordle": wordle_scores,
            "Connections": connections_scores,
            "Framed": framed_scores,
            "Gisnep": gisnep_scores,
            "Bandle": bandle_scores,
        }

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return {}


def get_monthly_scores():
    """Fetch total scores for all games for the past month."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    first_day_of_month = (
        datetime.utcnow()
        .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        .strftime("%Y-%m-%d %H:%M:%S")
    )

    try:
        # Wordle
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM wordle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (first_day_of_month,),
        )
        wordle_scores = cursor.fetchall()

        # Connections
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM connections_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (first_day_of_month,),
        )
        connections_scores = cursor.fetchall()

        # Framed
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM framed_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (first_day_of_month,),
        )
        framed_scores = cursor.fetchall()

        # Gisnep (rank by shortest average time)
        cursor.execute(
            """
            SELECT display_name, AVG(completion_time) AS avg_time
            FROM gisnep_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY avg_time ASC
        """,
            (first_day_of_month,),
        )
        gisnep_scores = cursor.fetchall()

        # Bandle
        cursor.execute(
            """
            SELECT display_name, SUM(total_score) AS total_score
            FROM bandle_scores
            WHERE timestamp >= ?
            GROUP BY display_name
            ORDER BY total_score DESC
        """,
            (first_day_of_month,),
        )
        bandle_scores = cursor.fetchall()

        conn.close()

        return {
            "Wordle": wordle_scores,
            "Connections": connections_scores,
            "Framed": framed_scores,
            "Gisnep": gisnep_scores,
            "Bandle": bandle_scores,
        }

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return {}


# Database functions for tracking roles (add these to your database.py file)
def save_user_role(user_id, role_name, game_number, expires_at):
    """Save information about a role granted to a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO user_roles 
        (user_id, role_name, game_number, expires_at) 
        VALUES (?, ?, ?, ?)
    """,
        (user_id, role_name, game_number, expires_at),
    )
    conn.commit()
    conn.close()


def get_expired_roles():
    """Get all expired roles that need to be removed."""
    now = datetime.datetime.now(cet_timezone).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_id, role_name FROM user_roles
        WHERE expires_at < ?
    """,
        (now,),
    )
    expired_roles = cursor.fetchall()
    conn.close()
    return expired_roles


def delete_expired_roles():
    """Delete records of expired roles from the database."""
    now = datetime.datetime.now(cet_timezone).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM user_roles WHERE expires_at < ?
    """,
        (now,),
    )
    conn.commit()
    conn.close()


def get_overall_recent_wordle_scores(limit=5):
    """
    Fetches the most recent Wordle scores from all users, ordered by timestamp descending,
    limited to the specified number.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT game_number, attempts, skill, luck, timestamp
            FROM wordle_scores
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )
        scores = cursor.fetchall()
        return scores
    except sqlite3.Error as e:
        print(f"Database error in get_overall_recent_wordle_scores: {e}")
        return []  # Return empty list in case of error
    finally:
        conn.close()


def get_overall_recent_connections_puzzle_number(limit=5):
    """
    Fetches the most recent Connections puzzle numbers from all users,
    ordered by timestamp descending, limited to the specified number.
    Returns a list of tuples, each containing (puzzle_number, timestamp).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT puzzle_number, timestamp
            FROM connections_scores
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )
        puzzles = cursor.fetchall()
        return puzzles
    except sqlite3.Error as e:
        print(f"Database error in get_overall_recent_connections_puzzle_number: {e}")
        return []  # Return empty list in case of error
    finally:
        conn.close()


def get_latest_game_number_from_db(game_name):
    """Fetches the latest game number from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT latest_number FROM latest_game_numbers WHERE game_name = ?",
        (game_name,),
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0
    print(f"DB: Retrieved latest_number for {game_name} = {latest_number}")  # DEBUGGING


def update_latest_game_number_in_db(game_name, latest_number):
    """Updates the latest game number in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO latest_game_numbers (game_name, latest_number) VALUES (?, ?)",
        (
            game_name,
            latest_number,
        ),
    )
    conn.commit()
    conn.close()
    print(f"DB: Updated latest_number for {game_name} to {latest_number}")  # DEBUGGING
