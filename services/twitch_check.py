import os

import twitchio
from twitchio.ext import eventsub, commands

from dotenv import load_dotenv
load_dotenv()

TARGET_USERNAME = os.getenv('TWITCH_TARGET_USERNAME')
WEBHOOK_URL = os.getenv('TWITCH_WEBHOOK_URL')
CALLBACK_URL = os.getenv('TWITCH_CALLBACK_URL')
APP_ID = os.getenv('TWITCH_APP_ID')
APP_SECRET = os.getenv('TWITCH_APP_SECRET')


TWITCH_CHANNEL_ID = os.getenv('TWITCH_CHANNEL_ID')


esbot = commands.Bot.from_client_credentials(client_id=APP_ID,
                                         client_secret=APP_SECRET)
esclient = eventsub.EventSubClient(esbot,
                                   webhook_secret=APP_SECRET,
                                   callback_route=CALLBACK_URL)
# when subscribing (you can only await inside coroutines)

eventsub_client.subscribe_channel_subscriptions(TWITCH_CHANNEL_ID)

@esbot.event()
async def eventsub_notification_subscription(payload: eventsub.ChannelSubscribeData):
    print('Received event!')
    channel = esbot.get_channel('channel')
    await channel.send(f'{payload.data.user.name} followed woohoo!')

esbot.loop.create_task(eventsub_client.listen(port=4000))
esbot.loop.create_task(esbot.start())
esbot.loop.run_forever()