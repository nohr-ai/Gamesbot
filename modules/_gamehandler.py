import re
import inspect

import discord
from discord import app_commands
from discord.ext import commands, tasks

__all__ = ["GenericGameHandler"]


class GenericGameHandler(commands.Cog):
    """
    Base class for all game handlers
    DEPRECATE: Hard to combine cogs and dispatch pattern, need to have a think....
    """

    def __init__(self, bot: commands.Bot, prefix: str) -> None:
        self.bot = bot
        self.prefix = prefix

    async def reply(self, input, response):
        if self.reply_private:
            message = await input.author.send(response)
        else:
            message = await input.channel.send(response)
        return message

    async def dispatch(self, message: discord.Message):
        if isinstance(message, discord.Message):
            result = re.match("^([a-zZ-a]*)", message.content)
            print(result)
            if result:
                # Group will be first word in message(word == game)
                group = result.group(1)
                print(group)
                for name, method in inspect.getmembers(
                    self, predicate=inspect.ismethod
                ):
                    # If we handle this game, exec!
                    if name == self.prefix + group:
                        await method(message)
        # if isinstance(message, discord.RawReactionActionEvent):
        #     match message.event_type:
        #         case "REACTION_ADD":
        #             for name, method in inspect.getmembers(
        #                 self, predicate=inspect.ismethod
        #             ):
        #                 if name == self.reaction_prefix + "add":
        #                     await method(message, permission)
        #         case "REACTION_REMOVE":
        #             for name, method in inspect.getmembers(
        #                 self, predicate=inspect.ismethod
        #             ):
        #                 if name == self.reaction_prefix + "remove":
        #                     await method(message, permission)
