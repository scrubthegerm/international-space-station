from discord.ext import commands
import discord
import config
import json
from requests import Session
import dateutil.parser as parser

session = Session()


class Space(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def apod(self, ctx):
        """Get NASA's Astronomy Picture of the Day!"""
        request = json.loads(session.get(f"https://api.nasa.gov/planetary/apod?api_key={config.nasa_api_key}").text)
        title = request['title']
        if "copyright" in request:
            title += f" by {request['copyright']}"
        embed = discord.Embed(title=title, description=request['explanation'], color=0x000000, url=request['hdurl'])
        embed.set_author(name="Astronomy Picture of the Day", icon_url=self.bot.user.avatar_url)
        embed.set_image(url=request['url'])
        await ctx.send(embed=embed)

    @commands.command(aliases=['mw', 'mweather', 'marsw'])
    async def marsweather(self, ctx, *, arg: str = None):
        """Get the weather on Mars."""
        request = json.loads(session.get(f"http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/"
                                         f"api.php").text)
        sol = ''
        embed = discord.Embed(title="Data obtained from REMS on the Curiosity rover.", color=0x000000)
        embed.set_thumbnail(url="https://space.is-for.me/i/gsre.png")

        if arg is None:
            sol = request['soles'][0]
            embed.set_footer(text="Note: This is the most recent weather data. Weather data is only sent once in "
                                  "a while. You can, however, look at weather for certain dates by searching their "
                                  "Mars sol or Earth date with this command.")
        else:
            for idx, d in enumerate(request['soles']):
                if d['sol'] == arg:
                    sol = request['soles'][idx]
                    break
                else:
                    pass
            # If it's not a sol, check if it's an earth date
            if sol is '':
                try:
                    parsed_date = parser.parse(arg).date().isoformat()
                    for idx, d in enumerate(request['soles']):
                        if d['terrestrial_date'] == parsed_date:
                            sol = request['soles'][idx]
                            break
                        else:
                            pass
                except ValueError:
                    pass
        if sol is '':
            await ctx.send(f"**Error:** Your argument couldn't be parsed as a valid Mars sol or Earth date. Proper "
                           f"sols range from {request['soles'][-1]['sol']} to {request['soles'][0]['sol']}. Proper "
                           f"dates range from {request['soles'][-1]['terrestrial_date']} to "
                           f"{request['soles'][0]['terrestrial_date']}.")
        else:
            max_temp_f = int(9.0 / 5.0 * int(sol['max_temp']) + 32)
            min_temp_f = int(9.0 / 5.0 * int(sol['min_temp']) + 32)
            embed.set_author(name=f"Weather on Mars for Sol {sol['sol']}",
                             icon_url=self.bot.user.avatar_url)
            embed.add_field(name="Mars sol", value=sol['sol'], inline=True)
            embed.add_field(name="Earth date", value=sol['terrestrial_date'], inline=True)
            embed.add_field(name="Season", value=sol['season'], inline=True)
            embed.add_field(name="Solar longitude", value=sol['ls'], inline=True)
            embed.add_field(name="High temperature", value=f"{sol['max_temp']}°C, {max_temp_f}°F", inline=True)
            embed.add_field(name="Low temperature", value=f"{sol['min_temp']}°C, {min_temp_f}°F", inline=True)
            embed.add_field(name="Pressure", value=f"{sol['pressure']} pascals", inline=True)
            embed.add_field(name="Relative humidity", value=sol['abs_humidity'], inline=True)
            embed.add_field(name="Wind speed", value=sol['wind_speed'], inline=True)
            embed.add_field(name="Wind direction", value=sol['wind_direction'], inline=True)
            embed.add_field(name="Sunrise", value=sol['sunrise'], inline=True)
            embed.add_field(name="Sunset", value=sol['sunset'], inline=True)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Space(bot))
