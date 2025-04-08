import discord
from discord.ext import commands, tasks
from discord import app_commands
import discord.ext

from ._gamehandler import GenericGameHandler
import database

_all__ = ["ScoreHandler"]


class ScoreHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @app_commands.command(
    #     name="myscore", description="Show user's last 5 wordle scores"
    # )
    # async def myscore(self, interaction: discord.Interaction):
    #     """Show the user's last 5 Wordle scores."""
    #     user = interaction.user.id
    #     scores = database.execute_db_command(
    #         """
    #             SELECT game_number, attempts, skill, luck, timestamp
    #             FROM wordle_scores
    #             WHERE user_id = ?
    #             ORDER BY timestamp DESC
    #             LIMIT ?
    #         """,
    #         (user, 5),
    #         get=5,
    #     )

    #     if not scores:
    #         await interaction.response.send_message(
    #             "No Wordle scores recorded for you yet!"
    #         )
    #     else:
    #         message = f"📊 *{interaction.user.display_name}'s last 5 Wordle scores**\n"
    #         for game_number, attempts, skill, luck, timestamp in scores:
    #             message += f"📅 {timestamp[:10]} | **Game {game_number}** — {attempts}/6 | Skill: {skill}/99 | Luck: {luck}/99\n"

    #     # message = f"📊 **{ctx.author.display_name}'s Last 5 Wordle Scores**\n"
    #     # for game_number, attempts, skill, luck, timestamp in scores:
    #     #     message += f"📅 {timestamp[:10]} | **Game {game_number}** — {attempts}/6 | Skill: {skill}/99 | Luck: {luck}/99\n"

    #     await interaction.response.send_message(message)

    def get_leaderboard(self, game: str, limit: int = 10):
        match game:
            case "wordle" | "framed":
                database.execute_db_command(
                    f"""
                    SELECT display_name, MAX(total_score) AS best_score
                    FROM {game}_scores
                    GROUP BY display_name
                    ORDER BY best_score DESC
                    LIMIT {limit}
                    """,
                    get=limit,
                )
            case "connections" | "bandle":
                database.execute_db_command(
                    f"""
                    SELECT display_name, SUM(total_score) AS total_score
                    FROM {game}_scores
                    GROUP BY display_name
                    ORDER BY total_score DESC
                    LIMIT {limit}
                    """
                )
            case "gisnep":
                database.execute_db_command(
                    f"""
                        SELECT display_name, AVG(completion_time) AS avg_time, COUNT(*) AS games_played
                        FROM {game}_scores
                        GROUP BY display_name
                        ORDER BY avg_time ASC, games_played DESC
                        LIMIT {limit}
                    """,
                    get=limit,
                )

    # @app_commands.command(
    #     name="leaderboard",
    #     description="Display the leaderboard for Wordle or Connections.",
    # )
    # async def leaderboard(self, interaction: discord.Interaction, game: str = "wordle"):
    #     """Display the leaderboard for Wordle or Connections."""
    #     game = game.lower()
    #     print(game)
    #     try:
    #         leaderboard = self.get_leaderboard(game, limit=10)
    #         leaderboard_message = f"🏆 **{game} Leaderboard** 🏆\n"
    #         for i, (player, best_score) in enumerate(leaderboard, 1):
    #             leaderboard_message += f"{i}. {player} - {best_score} points\n"
    #         await interaction.response.send_message(leaderboard_message)
    #     except ValueError:
    #         await interaction.response.send_message(
    #             "Invalid game choice! Use 'wordle' or 'connections'."
    #         )
    #     finally:
    #         return


async def setup(bot):
    """
    :meta private:
    """
    await bot.add_cog(ScoreHandler(bot))
