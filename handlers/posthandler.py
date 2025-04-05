import os
import discord
from discord import app_commands
from discord.ext import commands, tasks


class PostHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="Post_scores",
        description="Post scores for the given period (weekly or monthly) to the 'leaderboards' channel.",
    )
    async def post_scores(period: str):
        """Post scores for the given period (weekly or monthly) to the 'leaderboards' channel."""
        # Fetch scores from the database
        if period == "weekly":
            scores_by_game = database.get_weekly_scores()
        elif period == "monthly":
            scores_by_game = database.get_monthly_scores()
        else:
            raise ValueError("Invalid period. Use 'weekly' or 'monthly'.")

        # Find the 'leaderboards' channel
        leaderboard_channel = discord.utils.get(
            bot.get_all_channels(), name="leaderboards"
        )
        if not leaderboard_channel:
            print("Warning: Could not find the 'leaderboards' channel.")
            return

        # Iterate over each game and post scores
        for game, scores in scores_by_game.items():
            if not scores:
                continue

            message = f"**📅 {period.capitalize()} {game} Leaderboard**\n"
            for i, (player, score) in enumerate(scores, 1):
                message += f"{i}. {player}: {score} points\n"

            try:
                await leaderboard_channel.send(message)
                print(f"{period.capitalize()} {game} leaderboard posted.")
            except Exception as e:
                print(f"Error posting {period} {game} leaderboard: {e}")

    @post_scores.autocomplete("Period")
    async def post_scores_autocomplete(
        self, interaction: discord.Interaction, period: str
    ):
        valid_periods = ["weekly", "monthly"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in valid_periods
            if choice.lower().startswith(period.lower())
        ]

    @tasks.loop(time=datetime.time(hour=23, minute=59, second=50, tzinfo=CET_TIMEZONE))
    async def check_weekly_scores():
        """Post weekly leaderboards on Sunday."""
        if datetime.datetime.now(CET_TIMEZONE).weekday() == 6:  # Sunday
            await post_scores("weekly")

    @tasks.loop(time=datetime.time(hour=0, minute=1, second=0, tzinfo=CET_TIMEZONE))
    async def check_monthly_scores():
        """Post monthly leaderboards on the first of the month."""
        if datetime.datetime.now(CET_TIMEZONE).day == 1:
            await post_scores("monthly")
