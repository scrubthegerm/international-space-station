from discord.ext import commands
import discord
import config


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pong!"""
        await ctx.send("Pong!")

    @commands.command()
    async def invite(self, ctx):
        """Get an invite link for the bot."""
        await ctx.send(config.bot_oauth2_invite)

    @commands.command(aliases=['info', 'information'])
    async def about(self, ctx):
        """See some basic information about the bot."""
        developers = ""
        for d in config.dev_ids:
            dev = self.bot.get_user(d)
            developers += f"{dev.name}#{dev.discriminator}\n"
        embed = discord.Embed(title="Basic information about the bot", color=0x000000)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url="https://space.is-for.me/i/zots.jpg")
        embed.add_field(name="Developers", value=developers, inline=True)
        embed.add_field(name="Total guilds", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Total channels", value=f"{sum((1 for c in self.bot.get_all_channels()))}", inline=True)
        embed.add_field(name="Total users", value=f"{sum(1 for c in self.bot.users)}", inline=True)
        embed.add_field(name="Support guild invite", value=config.bot_guild_invite, inline=True)
        embed.add_field(name="OAuth2 invite", value=config.bot_oauth2_invite, inline=True)
        embed.set_footer(text="Happy spotting!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
