from discord import HTTPException
from discord.ext import commands
import checks
import config
import sqlite3


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_dev()
    async def eval(self, ctx, *, code):
        await ctx.send(f"`{eval(code)}`")

    @commands.command(hidden=True)
    async def ding(self, ctx):
        """bad inside joke"""
        await ctx.send("Dong!")

    @commands.command()
    @checks.is_dev()
    async def blockguild(self, ctx, guild_id: int, *, reason: str = "No reason provided..."):
        db = sqlite3.connect('data.db')
        c = db.cursor()
        try:
            c.execute(f"INSERT INTO blocked_guilds VALUES (?, ?)", (guild_id, reason))
            db.commit()
            db.close()
        except sqlite3.Error as e:
            await ctx.send(f"**Error:** Something went wrong: ```{e}```")
        guild = self.bot.get_guild(guild_id)
        if guild is not None:
            try:
                await guild.owner.send(f":no_entry: Sorry, your guild ({guild}) has been blocked from using the "
                                       f"International Space Station bot.\n\nReason: {reason}\n\nTo appeal, join the"
                                       f" bot support server at " + config.bot_guild_invite)
                await guild.leave()
            except HTTPException:
                await ctx.send("**Error:** Couldn't leave the guild!")
        await ctx.send("**Success:** Guild blocked.")


def setup(bot):
    bot.add_cog(Dev(bot))
