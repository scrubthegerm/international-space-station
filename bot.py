import discord
import sqlite3
import config
import checks
import asyncio
import json
from requests import Session
from discord.ext import commands


bot = commands.AutoShardedBot(command_prefix=config.prefix, description="International Space Station Bot", pm_help=None)

extensions = ["cogs.station", "cogs.info", "cogs.space", "cogs.agencies", "cogs.earth", "cogs.dev"]

db = sqlite3.connect('data.db')
c = db.cursor()

session = Session()


async def place_update():
    await bot.wait_until_ready()
    while not bot.is_closed():
        get_pos = json.loads(session.get(f"http://api.open-notify.org/iss-now.json").text)
        iss_lat = get_pos['iss_position']['latitude']
        iss_lon = get_pos['iss_position']['longitude']
        location = ''
        try:
            location = json.loads(session.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={iss_lat}"
                                              f"&lon={iss_lon}&zoom=0&namedetails=1").text)
        except json.JSONDecodeError:
            await bot.change_presence(status=type, activity=discord.Game(f"Currently over an unknown land!"
                                                                         f"({iss_lat}, {iss_lon})"))
        if "error" in location:
            await bot.change_presence(status=type, activity=discord.Game(f"Currently over the ocean \N{WATER WAVE} "
                                                                         f"({iss_lat}, {iss_lon})"))
        else:
            try:
                await bot.change_presence(status=type, activity=discord.Game(f"Currently over "
                                                                             f"{location['namedetails']['name:en']}! "
                                                                             f"({iss_lat}, {iss_lon})"))
            except KeyError:
                await bot.change_presence(status=type, activity=discord.Game(f"Currently over "
                                                                             f"{location['namedetails']['name']}! "
                                                                             f"({iss_lat}, {iss_lon})"))
            except Exception:
                await bot.change_presence(status=type, activity=discord.Game(f"Currently over an unknown land!"
                                                                             f"({iss_lat}, {iss_lon})"))

        await asyncio.sleep(30)


@bot.event
async def on_ready():
    c.execute('''CREATE TABLE IF NOT EXISTS `blocked_guilds` (
              `guild_id`	INTEGER,
              `reason`	TEXT);''')

    print("Connected as {}#{} [{}]\n=============".format(bot.user.name, bot.user.discriminator, bot.user.id))
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print("Whoops, couldn't load extension {}\n{}: {}".format(extension, type(e).__name__, e))

@bot.event
async def on_guild_join(guild):
    c.execute("SELECT reason FROM blocked_guilds WHERE guild_id = ?", (guild.id,))
    data = c.fetchone()
    if data is not None:
        await guild.owner.send(f":no_entry: Sorry, your guild is blocked from using the International Space Station"
                               f" bot.\nReason: {data}\nTo appeal, join the bot support server at "
                               f"{config.bot_guild_invite}")
        await guild.leave()
    else:
        channel = bot.get_channel(id=config.info_channel)
        embed = discord.Embed(title="New guild", color=0x228B22)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="Owner", value=f"{guild.owner.name}#{guild.owner.discriminator}", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Features", value=guild.features, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        await channel.send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    channel = bot.get_channel(id=config.info_channel)
    embed = discord.Embed(title="Left guild", color=0x8F1C1C)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Name", value=guild.name, inline=True)
    embed.add_field(name="Owner", value=f"{guild.owner.name}#{guild.owner.discriminator}", inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Features", value=guild.features, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    await channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Error:** That is not a valid command.")
        return
    if isinstance(error, commands.DisabledCommand):
        await ctx.send("**Error:** This command has been disabled.")
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**Error:** You do not have permission to use this command.")
        return
    if isinstance(error, checks.dev_only):
        await ctx.send("**Error:** That command can only be used by the bot developers.")
        return
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"**Error:** You're either missing an argument or have too many. You need: `{error.param}`")
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("**Error:** Sorry, you can't use this bot in a DM.")
        return

bot.loop.create_task(place_update())
bot.run(config.token)
