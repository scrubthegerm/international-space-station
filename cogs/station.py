import json

import config
import discord
import feedparser
import geopy.distance
from discord.ext import commands
from requests import Session
from tzwhere import tzwhere
import time
from datetime import datetime, timezone
import pytz
from pycountry_convert import country_name_to_country_alpha2 as conv

import summary_parser as sp

loc_list = json.loads(open("location_list.json", "r").read())

session = Session()


class Station(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tzwhere = tzwhere.tzwhere(forceTZ=True)

    @commands.command(aliases=['time', 'times'])
    async def search(self, ctx, *, arg):
        """Search for the next time the ISS will be visible from your city."""
        request = json.loads(session.get(f"https://nominatim.openstreetmap.org/search?format=json&q=\"{arg}\"").text)
        req_coord = f"{request[0]['lat']}, {request[0]['lon']}"
        tz = pytz.timezone(self.tzwhere.tzNameAt(float(request[0]['lat']), float(request[0]['lon']), forceTZ=True))
        shortest_distance = None
        index = None
        found = False
        for idx, f in enumerate(loc_list):
            distance = geopy.distance.vincenty(req_coord, f[1:3]).km
            if shortest_distance is None or distance < shortest_distance:
                shortest_distance = distance
                index = idx
        country = loc_list[index][4]
        subdiv = loc_list[index][3]
        city = loc_list[index][5]
        feed = feedparser.parse(f"https://spotthestation.nasa.gov/sightings/xml_files/{country}_{subdiv}_{city}.xml")
        for p in feed['entries']:
            if "ISS" in p['title']:
                x = p['summary']
                naive = datetime.strptime(f"{sp.get_datetime(x)}", "%A %b %d, %Y, %I:%M %p")
                local_dt = tz.localize(naive, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                real = utc_dt.replace(tzinfo=timezone.utc).timestamp()
                # This is so awful. Is there any better way to do this that actually gives the correct UTC timestamp?
                if real > time.time():
                    found = True
                    embed = discord.Embed(title="° = degrees over horizon. All times are local time.", color=0x000000)
                    embed.set_author(name=f"Next ISS sighting opportunity for {city.replace('_', ' ')}, "
                                          f"{country.replace('_', ' ')}",
                                     icon_url=self.bot.user.avatar_url)
                    embed.set_thumbnail(url=f"https://www.countryflags.io/{conv(country.replace('_', ' '))}"
                                            f"/flat/64.png")
                    embed.add_field(name="Time", value=f"{sp.get_datetime(x)}", inline=True)
                    embed.add_field(name="Visibility time", value=f"{sp.get_duration(x)}", inline=True)
                    embed.add_field(name="Maximum Height", value=f"{sp.get_max_height(x)}", inline=True)
                    embed.add_field(name="Appears", value=f"{sp.get_appear(x)}", inline=True)
                    embed.add_field(name="Disappears", value=f"{sp.get_disappear(x)}", inline=True)
                    embed.set_footer(text="Happy spotting!")
                    await ctx.send(embed=embed)
                    break
        if found is False:
            await ctx.send("Looks like NASA hasn't put up any future sightings for your town. Sorry! :slight_frown:")

    @commands.command(aliases=['where', 'wherenow'])
    async def now(self, ctx):
        """See where the ISS is right now."""
        get_pos = json.loads(session.get("http://api.open-notify.org/iss-now.json").text)
        iss_lat = get_pos['iss_position']['latitude']
        iss_lon = get_pos['iss_position']['longitude']
        embed = discord.Embed(title=f"The International Space Station is currently over {iss_lat}, {iss_lon}.",
                              color=0x000000)
        embed.set_image(
            url=f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/static/pin-l-triangle+ff00fc"
                f"({iss_lon},{iss_lat})/{iss_lon},{iss_lat},3,0/600x500@2x?access_token={config.mapbox_api_key}")
        embed.set_author(name="Current location of the International Space Station",
                         icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Happy spotting!")

        await ctx.send(embed=embed)

    @commands.command(aliases=['stream'])
    async def camera(self, ctx):
        """Get a view from the ISS's official livestream."""
        chan = json.loads(session.get("https://api.ustream.tv/channels/17074538.json").text)
        embed = discord.Embed(title=f"Want to see the ISS's official livestream? Click here.", color=0x000000,
                              url="https://eol.jsc.nasa.gov/ESRS/HDEV/", description="If the image is totally black"
                              ", that means the ISS is currently over an area where it is night-time.")
        embed.set_image(url=f"{chan['channel']['thumbnail']['live'].replace('192x108', '640x360')}?{time.time()}")
        # This is kinda horrible, but it's necessary to get an updated image.
        embed.set_author(name="Still image from a camera aboard the ISS",
                         icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Happy spotting!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Station(bot))
