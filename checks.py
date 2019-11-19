import discord
import config

from discord.ext import commands


class dev_only(commands.CommandError):
    pass


def is_dev():
    def predicate(ctx):
        if ctx.author.id in config.dev_ids:
            return True
        else:
            raise dev_only
    return commands.check(predicate)
