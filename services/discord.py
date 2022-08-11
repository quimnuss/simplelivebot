import random
import asyncio
import logging
from typing import List
from urllib import request
import discord
from discord.ext import commands
from config.config import *

from services.twitch import Twitch

from main import unsubscribe_all

role_name = 'streamer'
control_channels_ids = []
live_channels_ids = []

control_channels_names = []

servers = ['Gaming.cat', 'The Chuckle']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


def in_control_channel(func):
    async def inner(ctx, *args, **kwargs):
        if ctx.channel.id not in control_channels_ids:
            msg = f"Wrong channel for commands. Got {ctx.channel.name}, expecting {control_channels_names}"
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
    logging.info(f'{bot.user.name} has connected to Discord!')
    activity = discord.Activity(
        name="streamers en català",
        type=discord.ActivityType.watching,
        state="Streamers en Català"
    )
    await bot.change_presence(activity=activity)
    for guild in bot.guilds:

        if CONTROL_CHANNEL_ID:
            control_channel: discord.TextChannel = discord.utils.get(
                guild.text_channels, id=int(CONTROL_CHANNEL_ID))

        if not control_channel and CONTROL_CHANNEL_NAME:
            control_channel: discord.TextChannel = discord.utils.get(
                guild.text_channels, name=CONTROL_CHANNEL_NAME)

        if not control_channel:
            control_channel = guild.text_channels[0]
            logging.error(
                f"No control channel id specified or found. Selecting {control_channel.name}")

        control_channels_ids.append(control_channel.id)
        control_channels_names.append(control_channel.name)

        if LIVE_CHANNEL_ID:
            live_channel: discord.TextChannel = discord.utils.get(
                guild.text_channels, id=int(LIVE_CHANNEL_ID))

        if not live_channel and LIVE_CHANNEL_NAME:
            live_channel: discord.TextChannel = discord.utils.get(
                guild.text_channels, name=LIVE_CHANNEL_NAME)

        if not live_channel:
            live_channel = control_channel
            logging.error(
                f"No live channel id specified or found (id, name) ({LIVE_CHANNEL_ID}, {LIVE_CHANNEL_NAME}). Selecting {live_channel.name}")

        live_channels_ids.append(live_channel.id)
        await notify_control("I'm live!")
        # await notify("I'm live and I'll notify here!")


@bot.command(name='kill', help='kills the bot')
@commands.has_permissions(administrator=True)
@in_control_channel
@in_our_servers
async def quit(ctx):
    await ctx.send("Shutting down the bot")
    return await bot.logout()  # this just shuts down the bot.


@bot.command(name='streamers', help='lists the streamers with notifies')
@in_control_channel
async def list_all_streamers(ctx):

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    usernames, statuses = twitch.get_subscribed_usernames()

    logging.info(f'usernames: {usernames} statuses: {statuses}')

    failed_statuses = [
        f'{username}: {status}' for username, status in statuses.items() if status != 'enabled']

    streamers_msg = '\n'.join(usernames)
    failed_msg = '\n'.join(failed_statuses)
    msg = f'**🍿 Streamers:**\n\n{streamers_msg}' + \
        (f'\n\nFailed subscriptions (╯°□°）╯︵ ┻━┻ :\n{failed_msg}' if failed_statuses else '')
    await ctx.send(msg)


@bot.command(name='addstreamer', help='add a streamer for live notifies. e.g. !addstreamer clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_control_channel
@in_our_servers
async def add_streamer(ctx: commands.Context, twitch_username: str):

    if not twitch_username:
        await ctx.send(f"username cannot be empty {twitch_username}")
        return

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    usernames, statuses = twitch.get_subscribed_usernames()

    if twitch_username in usernames and statuses.get(twitch_username, None) == 'enabled':
        msg = f'{twitch_username} already has a subscription {statuses.get(twitch_username, None)}. Skipping!'
    else:

        try:
            result = twitch.subscribe(twitch_username=twitch_username.lower())
            msg = f'Subscribed to https://twitch.tv/{twitch_username} live notifications'
            logging.info(msg)
            logging.info(f'Result: {result}')
        except Exception as e:
            logging.exception(e)
            msg = f"Cancelling subscription since channel_id for {twitch_username} wasn't found. Exception: {e}"
            logging.error(msg)

    await ctx.send(msg)


@bot.command(name='addstreamers', help='add several streamers for live notifies. e.g. !addstreamer clicli gaming_catala')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_control_channel
@in_our_servers
async def add_streamers(ctx: commands.Context, *args):
    twitch_usernames: List[str] = list(args)
    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    usernames, statuses = twitch.get_subscribed_usernames()

    for twitch_username in twitch_usernames:
        if twitch_username in usernames and statuses.get(twitch_username, None) == 'enabled':
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

        # TODO fire and forget and gather the tasks at the end
        await ctx.send(msg)


@bot.command(name='removestreamer', help='remove a streamer for live notifies. e.g. !removestreamer clicli')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_control_channel
@in_our_servers
async def remove_streamer(ctx: commands.Context, twitch_username: str):

    if not twitch_username:
        await ctx.send(f"username cannot be empty {twitch_username}")
        return

    twitch = Twitch(app_id=APP_ID, app_secret=APP_SECRET,
                    callback_url=TWITCH_CALLBACK_URL)

    response = twitch.unsubscribe(twitch_username=twitch_username.lower())
    if response.ok:
        msg = f'Removed https://www.twitch.tv/{twitch_username} from subscriptions'
    else:
        msg = response.json()

    await ctx.send(msg)


@bot.command(name='clear', help='clear streamer subscriptions. e.g. !clear')
# @commands.has_role("Moderadors")
@commands.has_permissions(administrator=True)
@in_control_channel
@in_our_servers
async def clear(ctx):

    unsubscribe_all()

    msg = f'subscriptions cleared'

    await ctx.send(msg)


@bot.command(name='live', help='lists the streamers with notifies')
@in_control_channel
async def list_all_streamers(ctx, twitch_username: str):
    msg = f'📣 https://www.twitch.tv/{twitch_username} comença el **directe!** 📣'
    await ctx.send(msg)


@bot.command(name='presence', help='sets the state to a specific channel')
@in_control_channel
async def set_presence(ctx, twitch_username: str):
    await update_presence(twitch_username)
    msg = f'📣 Vaig a mirar https://www.twitch.tv/{twitch_username} en **directe!** 📣'
    await ctx.send(msg)


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
@in_control_channel
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
    logging.info(live_channels_ids)
    for channel_id in live_channels_ids:
        channel = bot.get_channel(channel_id)
        await channel.send(msg)


async def notify_control(msg):
    logging.info(control_channels_ids)
    for channel_id in control_channels_ids:
        channel = bot.get_channel(channel_id)
        await channel.send(msg)


async def update_presence(username):
    activity = discord.Activity(
        name=f"{username}",
        type=discord.ActivityType.streaming,
        state=f"{username} en Català",
        url=f"https://twitch.tv/{username}"
    )
    await bot.change_presence(activity=activity)


async def shutdown_presence():
    await bot.change_presence(activity=discord.Activity(name="Dormint"))
