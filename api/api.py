import logging

import asyncio

from fastapi import FastAPI, Body, Header, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from typing import Union
from .schemas import (
    Subscription, TtvChallenge, TTVEventFollow, TTVEventLive, SubscriptionTTVEventArbitraryPayload
)

from services.discord import bot, notify, notify_control

from config.config import DISCORD_TOKEN

from api.utils import verify_message

app = FastAPI()


# From
# https://gist.github.com/haykkh/49ed16a9c3bbe23491139ee6225d6d09
# register an asyncio.create_task(client.start()) on app's startup event
#                                        ^ note not client.run()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(DISCORD_TOKEN))


@app.on_event("shutdown")
async def shutdown_event():
    await notify_control("shutting down")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url='/docs')

# test with twitch-cli
# twitch-cli_1.1.6_Linux_x86_64/twitch event verify-subscription subscribe -F http://localhost:8000 -s TWITCH_APP_SECRET

# TODO we could explore the redirect option to distinguish challenge and legit event
# https://stackoverflow.com/questions/62282100/fastapi-redirectresponse-custom-headers
# e.g. https://github.com/tiangolo/fastapi/issues/199
#


@app.post("/ttv_callback")
async def twitch_callback(request: Request, twitch_eventsub_message_type: Union[str, None] = Header(default=None), data=Body()):
    logging.info("We got a sub event!")
    logging.info(f'h: {request.headers}\nb:{data}')

    twitch_message_id = request.headers['Twitch-Eventsub-Message-Id']
    twitch_message_timestamp = request.headers['Twitch-Eventsub-Message-Timestamp']
    twitch_message_signature = request.headers['Twitch-Eventsub-Message-Signature']

    body_str = await request.body()
    is_verified = verify_message(
        twitch_message_id, twitch_message_timestamp, twitch_message_signature, body_str)

    if not is_verified:
        logging.warning(
            f"Message {request.headers['twitch-eventsub-message-id']} did not pass the hmac verification")
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature mismatch"
        )

    if twitch_eventsub_message_type == 'webhook_callback_verification':
        ttv_challenge = TtvChallenge(**data)
        return PlainTextResponse(str(ttv_challenge.challenge))

    if twitch_eventsub_message_type == 'notification':
        esubwevent = SubscriptionTTVEventArbitraryPayload(**data)
        if esubwevent.subscription.type == 'channel.follow':
            follow_event = TTVEventFollow(**esubwevent.event)
            msg = f'https://www.twitch.tv/{follow_event.user_name} ha començat a seguir https://www.twitch.tv/{follow_event.broadcaster_user_name}!'
        elif esubwevent.subscription.type == 'stream.online':
            live_event = TTVEventLive(**esubwevent.event)
            msg = f'📣 https://www.twitch.tv/{live_event.broadcaster_user_name} comença el directe! 📣'
        else:
            logging.error(
                f'Unknown subscription type {esubwevent.subscription.type}')
            return
        logging.info(msg)
        await notify_control(msg)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
