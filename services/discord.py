import random
import asyncio
import logging
from typing import List
from urllib import request
import discord
from discord.ext import commands
from config.config import DISCORD_GUILD, APP_ID, APP_SECRET, TWITCH_CALLBACK_URL

from services.twitch import Twitch

from main import unsubscribe_all

role_name = 'streamer'
bot_channel = 'bot-control'
bot_channel_id = None

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

# TODO assume multiple guilds
# https://stackoverflow.com/questions/64841919/find-guild-id-in-on-ready-discord-py


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
async def list_all_streamers(ctx):

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    esublist = twitch.get_event_subscriptions()

    channel_ids = [
        subscription.condition.broadcaster_user_id
        for subscription in esublist.data
    ]

    ids_usernames = twitch.get_usernames_from_channel_ids(channel_ids)

    usernames = list(ids_usernames)

    streamers_msg = '\n'.join(usernames)

    msg = f'Streamers:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='addstreamer', help='add a streamer for live notifies. e.g. !addstreamer @CatSZekely#1234 clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
async def add_streamers(ctx, twitch_username: str, user: discord.Member = None):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    try:
        msg = twitch.subscribe(twitch_username=twitch_username)
    except Exception as e:
        logging.exception(e)
        logging.error("Continuing with insertion without twitch_id")
        msg = e

    await ctx.msg(msg)


@bot.command(name='removestreamer', help='remove a streamer for live notifies. e.g. !removestreamer clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
async def remove_streamer(ctx, twitch_username: str, user: discord.Member = None):

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    response = twitch.unsubscribe(twitch_username=twitch_username)
    if response.ok:
        msg = f'Removed https://www.twitch.tv/{twitch_username} from subscriptions'
    else:
        msg = response.json()

    await ctx.send(msg)


@bot.command(name='clear', help='clear streamer subscriptions. e.g. !clear')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
async def clear(ctx):

    unsubscribe_all()

    msg = f'subscriptions cleared'

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
