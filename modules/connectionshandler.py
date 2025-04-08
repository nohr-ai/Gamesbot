from __future__ import annotations
import discord
from discord.ext import commands, tasks
from discord import app_commands
from ._gamehandler import GenericGameHandler

import database

__all__ = ["ConnectionsHandler"]


class ConnectionsHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def calculate_score(self, guesses):
        base_points = {"🟪": 4, "🟦": 3, "🟩": 2, "🟨": 1}

        score = 0
        solved_first = ""
        first_group = False
        correct_guesses = 0
        mistakes = 0
        for guess in guesses:
            # Correct guesses
            print(guess)
            print(set(guess))
            if len(set(guess)) == 1:
                if not first_group:
                    first_group = guess[0]
                    print(f"first group: {first_group}")
                    # Why would we only care about purple and blue?
                    match first_group:
                        case "🟪":
                            solved_first = "🟪"
                            score += 2
                        case "🟦":
                            solved_first = "🟦"
                            score += 1
                        case "🟩":
                            solved_first = "🟩"
                        case "🟨":
                            solved_first = "🟨"
                correct_guesses += 1
                score += base_points[guess[0]]
            else:
                mistakes += 1

        if not mistakes:
            score += 5
        else:
            score -= mistakes

        return {
            "score": score,
            "guesses": len(guesses),
            "solved_first": solved_first,
            "finished_game": bool(correct_guesses),
        }

    def parse_game(self, message: discord.Message) -> dict:
        # TODO: error handling
        content = message.content
        lines = [line.strip() for line in content.split("\n")]
        if not lines[0].startswith("Connections") and not lines[1].startswith(
            "Puzzle #"
        ):
            print(f"Invalid connections header: {lines[0]}")
            return

        puzzle_number = int(lines[1].split("#")[1])
        print(puzzle_number)
        guesses = lines[2:]
        score = self.calculate_score(guesses)
        return {
            "user_id": message.author.id,
            "display_name": message.author.display_name,
            "puzzle_number": puzzle_number,
            **score,
        }

    def save_score(
        self,
        user_id,
        display_name,
        puzzle_number,
        guesses,
        score,
        solved_first,
        finished_game,
    ):
        database.save_connections_score(
            user_id,
            display_name,
            puzzle_number,
            score,
            guesses,
            solved_first,
            finished_game,
        )

    @commands.Cog.listener(name="on_message")
    async def connections_message(self, message: discord.Message):
        if message.author.bot:
            return
        print(f"{self.__cog_name__} cog")
        if message.content.startswith("Connections"):
            result = self.parse_game(message)
            print(result)
            for k, v in result.items():
                print(k, v)
            self.save_score(*result)
            latest_game = database.get_latest_game_number_from_db("Connections")
            if 


async def setup(bot):
    """
    :meta private:
    """
    await bot.add_cog(ConnectionsHandler(bot))
