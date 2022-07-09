import twitchio
from twitchio.ext import commands, eventsub
import time
import os
from dotenv import load_dotenv
load_dotenv()

TARGET_USERNAME = os.getenv('TWITCH_TARGET_USERNAME')
WEBHOOK_URL = os.getenv('TWITCH_WEBHOOK_URL')
CALLBACK_URL = os.getenv('TWITCH_CALLBACK_URL')
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')

# TODO get channel id from target_username
# meanwhile, here: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
TWITCH_CHANNEL_ID = os.getenv('TWITCH_CHANNEL_ID')

esbot = commands.Bot.from_client_credentials(client_id=APP_ID,
                                         client_secret=APP_SECRET)
esclient = eventsub.EventSubClient(esbot,
                                   webhook_secret=APP_SECRET,
                                   callback_route=CALLBACK_URL)

import requests

def get_token():
    params = {'client_id':APP_ID, 'client_secret':APP_SECRET, 'grant_type':'client_credentials'}
    response = requests.post(url='https://id.twitch.tv/oauth2/token', data=params)
    token = response.json()['access_token']
    return token

token = get_token()

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=token, prefix='!', initial_channels=['channel'])

    async def __ainit__(self) -> None:
        # self.loop.create_task(esclient.listen(port=8000))

        time.sleep(1)
        try:
            await esclient.subscribe_channel_follows(broadcaster=TWITCH_CHANNEL_ID)
        except twitchio.HTTPException as exp:
            print(f'Exception on subscribe: {exp.status} {exp.reason} {exp.message} {exp.args}')
            raise exp

    async def event_ready(self):
        print('Bot is ready!')


bot = Bot()
bot.loop.run_until_complete(bot.__ainit__())


@esbot.event()
async def event_eventsub_notification_follow(payload: eventsub.ChannelFollowData) -> None:
    print('Received event!')
    channel = bot.get_channel('channel')
    await channel.send(f'{payload.data.user.name} followed woohoo!')

bot.run()