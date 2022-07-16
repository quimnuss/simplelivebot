
from dataclasses import dataclass
import random
import asyncio
import logging
from typing import List
import discord
from discord.ext import commands
from common.creadors import CreadorsDb
from config.config import DISCORD_GUILD, DBFILE, APP_ID, APP_SECRET, TWITCH_CALLBACK_URL

from twitch import Twitch

from main import subscribe, unsubscribe

role_name = 'streamer'
bot_channel = 'bot-control'
bot_channel_id = None
streamers_role_id = None


streamers_db = CreadorsDb(DBFILE)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


def in_bot_channel(func):
    async def inner(ctx, *args, **kwargs):
        print(bot_channel_id)
        if ctx.channel.id is not bot_channel_id:
            logging.warning(
                f"Wrong channel for commands. Expecting {bot_channel}")
            return
        await func(ctx, *args, **kwargs)
    return inner


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel: discord.TextChannel = discord.utils.get(
        bot.get_all_channels(), guild__name=DISCORD_GUILD, name='bot-control')
    if not channel:
        return logging.error("The channel does not exist!")
    global bot_channel_id
    bot_channel_id = channel.id


@bot.command(name='streamers', help='lists the streamers with notifies')
@in_bot_channel
async def list_streamers(ctx):
    streamers: List[discord.Member] = discord.utils.get(
        ctx.guild.roles, name=role_name).members

    if not streamers:
        msg = f"I couldn't find any members in role {role_name}. It's an error :("
    else:
        streamers_list = [str(streamer) for streamer in streamers]
        streamers_in_db = streamers_db.get_streamers_by_discord_user(
            streamers_list)

        streamer_msg = [
            f'{discord_username} : {twitch_username}' for discord_username, twitch_username in streamers_in_db]

        streamers_msg = '\n'.join(streamer_msg)

        msg = f'Streamers:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='failstreamers', help='lists the streamers without linked twitch')
@in_bot_channel
async def list_incomplete_streamers(ctx):
    streamers = discord.utils.get(ctx.guild.roles, name=role_name).members

    if not streamers:
        msg = f"I couldn't find any members in role {role_name}. It's an error :("
    else:

        streamers_in_db = streamers_db.get_channel_streamers_without_twitch_username(
            ctx.guild.id)
        streamer_msg = [f'{discuser.name}' for discuser in streamers_in_db]

        streamers_msg = '\n'.join(streamer_msg)

        msg = f'Streamers without twitch:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='addstreamer', help='add a streamer for live notifies. e.g. !addstreamer @CatSZekely#1234 clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
async def add_streamers(ctx, user: discord.Member, twitch_username: str):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    try:
        twitch_user_uid = twitch.get_channel_id_from_username(
            username=twitch_username)
    except Exception as e:
        logging.exception(e)
        logging.error("Continuing with insertion without twitch_id")

    streamers_db.add_streamer(
        twitch_username, twitch_user_uid, user.name, user.id, ctx.guild.id)
    streamers_db[user.id] = twitch_username

    msg = f'Added {user.display_name} -> https://www.twitch.tv/{twitch_username} to db'

    subscribe(twitch_username=twitch_username)

    await ctx.send(msg)


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
@in_bot_channel
async def nine_nine(ctx):

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
