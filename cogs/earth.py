from discord.ext import commands
import discord
import config
import json
import datetime
import pytz
from requests import Session

session = Session()


def k_to_c(K):
    return round(K - 273.15)

def k_to_f(K):
    return round(k_to_c(K) * (9/5) + 32)


class Earth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['satimg'])
    async def coords(self, ctx, lat = 0.0, lon = 0.0, *, zoom: int = 3):
        """Locate a certain place on earth."""
        print(lat)
        print(lon)
        embed = discord.Embed(title=f"If this is zoomed in too far or isn't zoomed in enough, try including a zoom "
                                    f"level after the coordinates (default is 3).", color=0x000000)
        embed.set_image(url=f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/static/pin-l-triangle+ff00fc"
                            f"({lon},{lat})/{lon},{lat},{zoom},0/600x500@2x?access_token={config.mapbox_api_key}")
        embed.set_author(name=f"Location of \"{lat}, {lon}\" (zoom: {zoom})", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Happy spotting!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['satmar'])
    async def weather(self, ctx, *, arg):
        """Locate a certain place on earth."""
        request = json.loads(session.get(f"https://nominatim.openstreetmap.org/search?format=json&q=\"{arg}\"").text)
        req_lat = request[0]['lat']
        req_lon = request[0]['lon']

        w_return = json.loads(session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={req_lat}&lon={req_lon}&appid={config.owm_api_key}").text)
        embed = discord.Embed(title=f"Weather for {w_return['name']}, {w_return['sys']['country']}", color=0x000000)
        embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{w_return['weather'][0]['icon']}@4x.png")
        embed.set_author(name=f"{w_return['weather'][0]['main']}, {k_to_c(w_return['main']['temp'])}°C/{k_to_f(w_return['main']['temp'])}°F", icon_url=self.bot.user.avatar_url)
        embed.add_field(name="As of (local time)", value=f"{datetime.datetime.fromtimestamp(w_return['dt'] - abs(w_return['timezone']), tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')}", inline=True)
        embed.add_field(name="Temperature", value=f"{k_to_c(w_return['main']['temp'])}°C/{k_to_f(w_return['main']['temp'])}°F", inline=True)
        embed.add_field(name="Feels like", value=f"{k_to_c(w_return['main']['feels_like'])}°C/{k_to_f(w_return['main']['feels_like'])}°F", inline=True)
        embed.add_field(name="Humidity", value=f"{w_return['main']['humidity']}%", inline=True)
        embed.add_field(name="Pressure", value=f"{w_return['main']['pressure']} hPa", inline=True)
        embed.add_field(name="Wind speed", value=f"{w_return['wind']['speed']}", inline=True)
        embed.add_field(name="Sunrise", value=f"{datetime.datetime.fromtimestamp(w_return['sys']['sunrise'] - abs(w_return['timezone']), tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')}", inline=True)
        embed.add_field(name="Sunset", value=f"{datetime.datetime.fromtimestamp(w_return['sys']['sunset'] - abs(w_return['timezone']), tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')}", inline=True)
        embed.set_footer(text="If the location you searched for and the location you got were different, that's because there's no weather station where you searched so we went with the closest.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Earth(bot))
