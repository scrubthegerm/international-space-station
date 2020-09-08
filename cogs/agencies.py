from discord.ext import commands
import discord
import json
from requests import Session
import dateutil.parser as parser
from difflib import SequenceMatcher

session = Session()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Agencies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spacex", aliases=['spacex.launch', 'sx.launches', 'spacex.launches', 'sxlaunch', 'sx.launch'])
    async def spacex(self, ctx, *, arg: str = None):
        """Get basic information about SpaceX's most recent launch, or search past launches."""
        launch = None
        request = json.loads(session.get(f"https://api.spacexdata.com/v2/launches").text)
        # If the arg is nothing, just get the most recent launch
        if arg is None:
            launch = request[-1]
        else:
            # If the arg is a number, try to find a flight number
            try:
                if request[0]['flight_number'] <= int(arg) <= request[-1]['flight_number']:
                    launch = request[int(arg) - 1]
                else:
                    pass
            except ValueError:
                pass
            # If the arg is a date, find a flight by that date
            try:
                for idx, flight in enumerate(request):
                    if parser.parse(arg).date() == parser.parse(flight['launch_date_local']).date():
                        launch = request[idx]
                    else:
                        pass
            except (ValueError, OverflowError):
                pass
            # If the arg is a mission name, try to find that mission name
            try:
                for idx, flight in enumerate(request):
                    if arg.lower() == flight['mission_name'].lower():
                        launch = request[idx]
                        break
                    elif similar(arg.lower(), flight['mission_name'].lower()) >= 0.7:
                        launch = request[idx]
                        break
                    else:
                        pass
            except ValueError:
                pass
        # When all else fails...
        if launch is None:
            await ctx.send("**Error:** Couldn't determine a SpaceX launch from the information provided.\n\n"
                           f"You can search by flight number (currently {request[0]['flight_number']} to "
                           f"{request[-1]['flight_number']}), flight date, or mission name.")
        else:
            embed = discord.Embed(title=f"\N{ROCKET} {launch['mission_name']}", color=0x000000,
                                  description=launch['details'])
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=launch['links']['mission_patch'])
            embed.add_field(name="Time", value=parser.parse(launch['launch_date_local']), inline=True)
            embed.add_field(name="Rocket Name", value=launch['rocket']['rocket_name'], inline=True)
            embed.add_field(name="Launch Site", value=launch['launch_site']['site_name'], inline=True)
            embed.add_field(name="Launch Successful?", value=launch['launch_success'], inline=True)
            payload_num = 1
            for payload in launch['rocket']['second_stage']['payloads']:
                embed.add_field(name=f"Payload {payload_num} ID", value=payload['payload_id'], inline=True)
                embed.add_field(name=f"Payload {payload_num} Nationality", value=payload['nationality'], inline=True)
                embed.add_field(name=f"Payload {payload_num} Manufacturer", value=payload['manufacturer'], inline=True)
                embed.add_field(name=f"Payload {payload_num} Type", value=payload['payload_type'], inline=True)
                embed.add_field(name=f"Payload {payload_num} Mass",
                                value=f"{payload['payload_mass_kg']}kg ({payload['payload_mass_lbs']}lbs)", inline=True)
                embed.add_field(name=f"Payload {payload_num} Lifespan",
                                value=f"{payload['orbit_params']['lifespan_years']} years", inline=True)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Agencies(bot))
