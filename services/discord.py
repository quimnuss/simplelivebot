
from dataclasses import dataclass
import random
import asyncio
import logging
import discord
from discord.ext import commands

from config.config import DISCORD_GUILD

from main import subscribe, unsubscribe

role_name = 'streamer'
bot_channel = 'bot-control'
bot_channel_id = None
streamers_role_id = None


@dataclass
class Hawk:
    guild_id: int
    channel_id: int
    role_id: int


streamers_db = {}
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

hawks = {}


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel: discord.TextChannel = discord.utils.get(
        bot.get_all_channels(), guild__name=DISCORD_GUILD, name='bot-control')
    if not channel:
        return logging.error("The channel does not exist!")
    global bot_channel_id
    bot_channel_id = channel.id

    channel: discord.TextChannel = discord.utils.get(
        bot.get_all_channels(), guild__name=DISCORD_GUILD, name='bot-control')

    guild = channel.guild
    role: discord.Role = discord.utils.get(guild.roles, name=role_name)
    if role:
        hawks[guild.id] = Hawk(
            guild_id=guild.id, channel_id=channel.id, role_id=role.id)
    else:
        logging.error(f'Role {role_name} does not exist in {guild.name}')


@bot.command(name='streamers', help='lists the streamers with notifies')
async def list_streamers(ctx):
    if ctx.channel.id is not bot_channel_id:
        logging.warning(f"Wrong channel for commands. Expecting {bot_channel}")
        return

    streamers = discord.utils.get(ctx.guild.roles, name=role_name).members

    if not streamers:
        msg = f"I couldn't find any members in role {role_name}. It's an error :("
    else:

        streamer_msg = [
            f'{discuser.name} : {streamers_db.get(discuser.id, None)}' for discuser in streamers]

        streamers_msg = '\n'.join(streamer_msg)

        msg = f'Streamers:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='failstreamers', help='lists the streamers without linked twitch')
async def list_incomplete_streamers(ctx):
    if ctx.channel.id is not bot_channel_id:
        logging.warning(f"Wrong channel for commands. Expecting {bot_channel}")
        return

    streamers = discord.utils.get(ctx.guild.roles, name=role_name).members

    if not streamers:
        msg = f"I couldn't find any members in role {role_name}. It's an error :("
    else:

        streamer_msg = [
            f'{discuser.name} : {streamers_db.get(discuser.id, None)}' for discuser in streamers if discuser not in streamers_db]

        streamers_msg = '\n'.join(streamer_msg)

        msg = f'Streamers without twitch:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='addstreamer', help='add a streamer for live notifies. e.g. !addstreamer @CatSZekely#1234 clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
async def add_streamers(ctx, user: discord.Member, twitch_username: str):
    if ctx.channel.id is not bot_channel_id:
        logging.warning(f"Wrong channel for commands. Expecting {bot_channel}")
        return

    streamers_db[user.id] = twitch_username

    msg = f'Added {user.display_name} -> https://www.twitch.tv/{twitch_username} to db'

    subscribe(twitch_username=twitch_username)

    await ctx.send(msg)


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    if ctx.channel.id is not bot_channel_id:
        print(f"Wrong channel for commands. Expecting {bot_channel}")
        return
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


async def notify(msg):
    channel = bot.get_channel(bot_channel_id)
    await channel.send(msg)
