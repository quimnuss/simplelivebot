from pydantic import BaseModel, AnyHttpUrl
from typing import Union, Dict, List
from uuid import UUID
import datetime


class Transport(BaseModel):
    method: str
    callback: AnyHttpUrl


class Condition(BaseModel):
    broadcaster_user_id: int


class Subscription(BaseModel):
    id: UUID
    status: str
    type: str
    version: int
    condition: Condition
    transport: Transport
    created_at: datetime.datetime
    cost: int


class TTVEvent(BaseModel):
    broadcaster_user_id: int
    broadcaster_user_login: str
    broadcaster_user_name: str


class TTVEventFollow(TTVEvent):
    user_id: int
    user_login: str
    user_name: str
    followed_at: datetime.datetime


class TTVEventLive(TTVEvent):
    id: int
    type: str
    started_at: datetime.datetime


class SubscriptionPayloadBase(BaseModel):
    subscription: Subscription


class SubscriptionTTVEventArbitraryPayload(SubscriptionPayloadBase):
    event: Dict[str, str]


class SubscriptionTTVEventPayload(SubscriptionPayloadBase):
    event: TTVEvent


class SubscriptionTTVEventFollowPayload(SubscriptionPayloadBase):
    event: TTVEventFollow


class TtvChallenge(BaseModel):
    subscription: Subscription
    challenge: str


class EventSubList(BaseModel):
    total: int
    data: List[Subscription]


# hyphen to underscore swap requires some work
# https://medium.com/analytics-vidhya/camel-case-models-with-fast-api-and-pydantic-5a8acb6c0eee
#
# class TtvESHeaders(BaseModel):
#     host: str
#     user_agent: str
#     content_length: int
#     content_type: str
#     twitch_eventsub_message_id: UUID
#     twitch_eventsub_message_retry: int
#     twitch_eventsub_message_signature: str
#     twitch_eventsub_message_timestamp: datetime.datetime
#     twitch_eventsub_message_type: str
#     twitch_eventsub_subscription_type: str
#     twitch_eventsub_subscription_version: str
#     accept_encoding: str
