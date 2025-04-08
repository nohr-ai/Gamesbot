import os
import discord
import asyncio
import datetime
import zoneinfo
from discord.ext import commands, tasks
from typing import Dict, List, Tuple, Optional, Any
from dotenv import load_dotenv

# Import custom modules
import database
import score_parser
import game_config
import role_manager


class GamesBot(commands.Bot):
    """
    Main bot class
    """

    def __init__(self):
        self.timezone = zoneinfo.ZoneInfo(os.getenv("TIMEZONE", "Europe/Berlin"))
        intents = discord.Intents.all()
        intents.messages = True
        intents.guilds = True
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=os.getenv("COMMAND_PREFIX", "!"), intents=intents
        )
        self.handlers = []

        # Initialize db once, on_ready can be called every bot refresh/wakeup
        database.initialize_db()

        # # Start scheduled tasks
        # check_weekly_scores.start()
        # check_monthly_scores.start()
        # now = datetime.datetime.now(self.timezone)
        # if 6 == now.weekday():
        #     # Where TF is this shit defined?
        #     await post_weekly_scores()
        # elif 1 == now.day:
        #     await post_monthly_scores()

    # async def handler_setup(self):
    #     for handler, prefix in []:
    #         await self.add_cog(handler(self, prefix))

    async def setup_hook(self):
        """
        To perform asynchronous setup after the bot is logged in but before it has connected to the Websocket, overwrite this coroutine.
        This is only called once, in login(), and will be called before any events are dispatched, making it a better solution than doing such setup in the on_ready() event.
        """
        try:
            for handler in [
                "modules." + module.removesuffix(".py")
                for module in os.listdir("modules")
                if not module.startswith("_") and module.endswith(".py")
            ]:
                await self.load_extension(handler)
                print(handler)
        except Exception as e:
            print(f"Could not load {handler} : {e}")
        finally:
            print("syncing")
            await self.tree.sync()

    async def on_ready(self):
        """Handler for when the bot is ready."""
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        """Handler for new messages."""
        if message.author.bot:
            return  # Ignore bot messages
        # for handler in self.extensions.items():

        #     handler.dispatch(message)
        # content = message.content
        # processed = False

        # # Check if the message is in the 'scores' channel
        # if message.channel.name == "scores":
        #     # Check each game configuration
        #     for game_key, config in game_config.GAME_CONFIGS.items():
        #         if config["is_game_message"](content):
        #             print(
        #                 f"Detected {config['name']} message from {message.author.display_name}"
        #             )
        #             await handle_game_message(message, game_key, config)
        #             processed = True
        #             break

        # if not processed:
        #     await bot.process_commands(
        #         message
        #     )  # Process commands if not a game message

    # async def handle_game_message(message, game_key, game_config):
    #     """
    #     Handle a game message (Wordle, Connections, Framed, Gisnep, Bandle).

    #     Args:
    #         message: The Discord message
    #         game_key: The key for the game in the GAME_CONFIGS dictionary
    #         game_config: The game configuration dictionary
    #     """
    #     guild = message.guild
    #     member = message.author
    #     display_name = message.author.display_name
    #     user_id = message.author.id

    #     # Parse the message content
    #     game_info = game_config["parse_function"](message.content)

    #     if not game_info:
    #         await message.channel.send(
    #             f"⚠️ Couldn't process your {game_config['name']} result."
    #         )
    #         return

    #     # Save the score based on the game type
    #     if game_key == "wordle":
    #         game_config["save_score_function"](
    #             user_id,
    #             display_name,
    #             game_info["game_number"],
    #             game_info["attempts"],
    #             game_info.get("skill"),  # Use .get() to handle None values
    #             game_info.get("luck"),
    #             game_info.get("hard_mode", False),
    #         )

    #     elif game_key == "connections":
    #         game_config["save_score_function"](
    #             user_id,
    #             display_name,
    #             game_info["puzzle_number"],
    #             game_info["total_score"],
    #             game_info["num_guesses"],
    #             game_info["solved_purple_first"],
    #             game_info["solved_blue_first"],
    #         )

    #     elif game_key == "framed":
    #         game_config["save_score_function"](
    #             user_id,
    #             display_name,
    #             game_info["game_number"],
    #             game_info["attempts"],
    #             game_info["total_score"],
    #         )

    #     elif game_key == "gisnep":
    #         game_config["save_score_function"](
    #             user_id,
    #             display_name,
    #             game_info["game_number"],
    #             game_info["completion_time"],
    #         )

    #     elif game_key == "bandle":
    #         game_config["save_score_function"](
    #             user_id,
    #             display_name,
    #             game_info["game_number"],
    #             game_info["attempts"],
    #             game_info["total_score"],
    #             game_info["bonus_completed"],
    #             game_info["bonus_total"],
    #         )

    #     # Create the acknowledgement message
    #     response = game_config["create_acknowledgement"](display_name, game_info)

    #     # Get the latest game number from the database
    #     game_number_key = game_config[
    #         "game_number_key"
    #     ]  # Use game_number_key from config
    #     latest_game_number = game_config["get_latest_game_number_function"](
    #         game_config["name"]
    #     )
    #     print(  # DEBUGGING
    #         f"{game_config['name']}: Retrieved latest_game_number ="
    #         f" {latest_game_number}"
    #     )
    #     current_game_number = game_info[game_number_key]

    #     # If this is the latest game, update roles and notify
    #     if current_game_number >= latest_game_number:
    #         game_config["update_latest_game_number_function"](
    #             game_config["name"], current_game_number
    #         )
    #         print(  # DEBUGGING
    #             f"{game_config['name']}: Updated latest_game_number to"
    #             f" {game_number_key}"
    #         )

    #         # Handle role assignment
    #         success = await role_manager.handle_game_role_assignment(
    #             guild, member, game_config, current_game_number, latest_game_number
    #         )

    #         if success:
    #             chat_channel_name = game_config["chat_channel_name"]
    #             response += f"\n\n{member.mention} You now have access to the {chat_channel_name} channel!"
    #             await role_manager.introduce_player_in_game_channel(
    #                 guild, display_name, game_config, game_info
    #             )

    #     # Send the response message
    #     await message.channel.send(response)


if __name__ == "__main__":
    load_dotenv()
    GamesBot().run(os.getenv("TOKEN"))
    # bot.run(os.getenv("TOKEN"))
