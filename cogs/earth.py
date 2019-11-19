from discord.ext import commands
import discord
import config
import json
from requests import Session
import dateutil.parser as parser

session = Session()


class Earth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['satimg'])
    async def coords(self, ctx, lat = 0, lon = 0, *, zoom: int = 3):
        """Locate a certain place on earth."""
        embed = discord.Embed(title=f"If this is zoomed in too far or isn't zoomed in enough, try including a zoom "
                                    f"level after the coordinates (default is 3).", color=0x000000)
        embed.set_image(url=f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/static/pin-l-triangle+ff00fc"
                            f"({lon},{lat})/{lon},{lat},{zoom},0/600x500@2x?access_token={config.mapbox_api_key}")
        embed.set_author(name=f"Location of \"{lat}, {lon}\" (zoom: {zoom})", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Happy spotting!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Earth(bot))
