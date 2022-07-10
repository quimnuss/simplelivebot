import logging
import asyncio

from fastapi import FastAPI, Body, Header, Request
from fastapi.responses import PlainTextResponse
from typing import Union
from .schemas import (
    Subscription, TtvChallenge, TTVEventFollow, TTVEventLive, SubscriptionTTVEventArbitraryPayload
)

from services.discord import bot, notify

from config.config import DISCORD_TOKEN


app = FastAPI()


def challenge_process():
    # TODO test that the challenge is legit
    # https://dev.twitch.tv/docs/eventsub/handling-webhook-events/#verifying-the-event-message
    pass


# From
# https://gist.github.com/haykkh/49ed16a9c3bbe23491139ee6225d6d09
# register an asyncio.create_task(client.start()) on app's startup event
#                                        ^ note not client.run()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(DISCORD_TOKEN))


@app.get("/")
async def root():
    return {"message": "Hello World"}

# test with twitch-cli
# twitch-cli_1.1.6_Linux_x86_64/twitch event verify-subscription subscribe -F http://localhost:8000 -s TWITCH_APP_SECRET

# TODO we could explore the redirect option to distinguish challenge and legit event
# https://stackoverflow.com/questions/62282100/fastapi-redirectresponse-custom-headers
# e.g. https://github.com/tiangolo/fastapi/issues/199
#


@app.post("/ttv_callback")
async def root(request: Request, twitch_eventsub_message_type: Union[str, None] = Header(default=None), data=Body()):
    logging.info("We got a sub event!")
    logging.info(f'h: {request.headers}\nb:{data}')

    if twitch_eventsub_message_type == 'webhook_callback_verification':
        ttv_challenge = TtvChallenge(**data)
        return PlainTextResponse(str(ttv_challenge.challenge))

    if twitch_eventsub_message_type == 'notification':
        esubwevent = SubscriptionTTVEventArbitraryPayload(**data)
        if esubwevent.subscription.type == 'channel.follow':
            follow_event = TTVEventFollow(**esubwevent.event)
            msg = f'{follow_event.user_name} ha començat a seguir {follow_event.broadcaster_user_name}!'
            await notify(msg)
        elif esubwevent.subscription.type == 'stream.online':
            live_event = TTVEventLive(**esubwevent.event)
            msg = f'{live_event.broadcaster_user_name} comença el directe!'
            await notify(msg)


    return {"message": "Hello World"}


# @app.post("/")
# async def root(subchallenge: TtvChallenge, request: Request):
#     # we have to filter by header :(
#     # we can't use proper pydantic validation
#     return {subchallenge.challenge}
