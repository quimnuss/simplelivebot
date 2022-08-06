import random
import asyncio
import logging
from typing import List
from urllib import request
import discord
from discord.ext import commands
from config.config import APP_ID, APP_SECRET, TWITCH_CALLBACK_URL

from services.twitch import Twitch

from main import unsubscribe_all

role_name = 'streamer'
bot_channels = ['bot-control']
bot_channel_id = None

servers = ['Gaming.cat', 'The Chuckle']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


def in_bot_channel(func):
    async def inner(ctx, *args, **kwargs):
        print(bot_channel_id)
        if ctx.channel.name not in bot_channels:
            msg = f"Wrong channel for commands. Got {ctx.channel.name}, expecting {bot_channels}"
            logging.warning(msg)
            await ctx.send(msg)
            return
        await func(ctx, *args, **kwargs)
    return inner


def in_our_servers(func):
    async def inner(ctx, *args, **kwargs):
        if ctx.guild.name not in servers:
            msg = f"Server {ctx.guild.name} is not an authorized server {servers}"
            logging.warning(msg)
            await ctx.send(msg)
            return
        await func(ctx, *args, **kwargs)
    return inner


# TODO assume multiple guilds
# https://stackoverflow.com/questions/64841919/find-guild-id-in-on-ready-discord-py

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for guild in bot.guilds:
        channel: discord.TextChannel = discord.utils.get(
            guild.channels, name=bot_channels[0])
        channel.send("I'm live!")


@bot.command(name='kill', help='kills the bot')
@commands.has_permissions(administrator=True)
@in_bot_channel
@in_our_servers
async def quit(ctx):
    await ctx.send("Shutting down the bot")
    return await bot.logout()  # this just shuts down the bot.


@bot.command(name='streamers', help='lists the streamers with notifies')
@in_bot_channel
async def list_all_streamers(ctx):

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    usernames = twitch.get_subscribed_usernames()

    streamers_msg = '\n'.join(usernames)

    msg = f'Streamers:\n{streamers_msg}'
    await ctx.send(msg)


@bot.command(name='addstreamer', help='add a streamer for live notifies. e.g. !addstreamer clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
@in_our_servers
async def add_streamers(ctx: commands.Context, twitch_username: str):
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    usernames = twitch.get_subscribed_usernames()

    if twitch_username in usernames:
        msg = f'{twitch_username} already has a subscription. Skipping!'
    else:

        try:
            result = twitch.subscribe(twitch_username=twitch_username)
            msg = f'Subscribed to https://twitch.tv/{twitch_username} live notifications'
            logging.info(msg)
            logging.info(f'Result: {result}')
        except Exception as e:
            logging.exception(e)
            msg = f"Cancelling subscription since channel_id for {twitch_username} wasn't found. Exception: {e}"
            logging.error(msg)

    await ctx.send(msg)


@bot.command(name='removestreamer', help='remove a streamer for live notifies. e.g. !removestreamer clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_bot_channel
@in_our_servers
async def remove_streamer(ctx: commands.Context, twitch_username: str):

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
@in_our_servers
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
