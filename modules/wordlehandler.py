from __future__ import annotations
import discord
from discord.ext import commands, tasks
from discord import app_commands
from ._gamehandler import GenericGameHandler

import database

__all__ = ["WordleHandler"]


class WordleHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def save_score(
        self,
        user_id,
        display_name,
        game_number,
        attempts,
        skill=None,
        luck=None,
        hard_mode=False,
    ):
        """Save a new Wordle score with optional skill, luck, and hard mode flag."""
        score = 100 - ((attempts - 1) * 20)
        if score < 0:
            score = 0

        total_score = (skill or 0) + score - (luck or 0)

        database.execute_command(
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

    # @commands.Cog.listener(name="on_message")
    # async def on_message(self, message: discord.Message):
    #     if message.author.bot:
    #         return
    #     print("In wordle cog")
    #     content = message.content
    #     if message.content.startswith("Wordle"):
    #         database.save_wordle_score

    @app_commands.command(
        name="myscore", description="Show user's last 5 wordle scores"
    )
    async def myscore(self, interaction: discord.Interaction):
        """Show the user's last 5 Wordle scores."""
        user = interaction.user.id
        scores = database.execute_command(
            """
                SELECT game_number, attempts, skill, luck, timestamp
                FROM wordle_scores
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
            (user, 5),
            get=5,
        )

        if not scores:
            await interaction.response.send_message(
                "No Wordle scores recorded for you yet!"
            )
        else:
            message = f"📊 *{interaction.user.display_name}'s last 5 Wordle scores**\n"
            for game_number, attempts, skill, luck, timestamp in scores:
                message += f"📅 {timestamp[:10]} | **Game {game_number}** — {attempts}/6 | Skill: {skill}/99 | Luck: {luck}/99\n"

        # message = f"📊 **{ctx.author.display_name}'s Last 5 Wordle Scores**\n"
        # for game_number, attempts, skill, luck, timestamp in scores:
        #     message += f"📅 {timestamp[:10]} | **Game {game_number}** — {attempts}/6 | Skill: {skill}/99 | Luck: {luck}/99\n"

        await interaction.response.send_message(message)

    @app_commands.command(
        name="wordle_leaderboard",
        description="Fetch the top players for Wordle leaderboard.",
    )
    async def get_wordle_leaderboard(
        self, interaction: discord.Interaction, limit: int = 10
    ) -> None:
        """Fetch the top players for Wordle leaderboard."""
        leaderboard = database.execute_command(
            """
                SELECT display_name, MAX(total_score) AS best_score
                FROM wordle_scores
                GROUP BY display_name
                ORDER BY best_score DESC
                LIMIT 10
            """,
            get=limit,
        )
        leaderboard_message = f"🏆 **Wordle Leaderboard** 🏆\n"
        for i, (player, best_score) in enumerate(leaderboard, 1):
            leaderboard_message += f"{i}. {player} - {best_score} points\n"
        await interaction.response.send_message(leaderboard_message)


async def setup(bot):
    """
    :meta private:
    """
    await bot.add_cog(WordleHandler(bot))
