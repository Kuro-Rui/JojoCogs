# Copyright (c) 2021 - Jojo#7791
# Licensed under MIT

from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Union

import discord
from redbot.core import commands

__all__ = [
    "create_doc",
    "TimestampFormats",
    "timestamp_format",
    "NoneConverter",
    "InviteNoneConverter",
    "send_button",
]
NoneType = type(None)


def create_doc(default: str = None, *, override: bool = False):
    """Create a docstring if you don't wanna"""

    def inner(func):
        doc = default or "No Documentation"
        if not func.__doc__ or override:
            func.__doc__ = doc
        return func

    return inner


@create_doc()
class TimestampFormats(Enum):
    DEFAULT = "f"
    LONG_DATE_TIME = "F"
    SHORT_DATE = "d"
    LONG_DATE = "D"
    SHORT_TIME = "t"
    LONG_TIME = "T"
    RELATIVE_TIME = "R"


@create_doc()
def timestamp_format(dt: datetime = None, *, dt_format: TimestampFormats = None) -> str:
    if not dt:
        dt = datetime.now()
    if not dt_format or dt_format == TimestampFormats.DEFAULT:
        return f"<t:{int(dt.timestamp())}>"
    else:
        return f"<t:{int(dt.timestamp())}:{dt_format.value}>"


class NoneConverter(commands.Converter):
    """A simple converter for NoneType args for commands"""

    def __init__(self, *, strict: bool = False):
        self.strict = strict

    async def convert(self, ctx: commands.Context, arg: str) -> Union[NoneType, str]:
        args = ["none"]
        if not self.strict:
            args.extend(["no", "nothing"])
        if arg.lower() in args:
            return None
        return arg


class InviteNoneConverter(NoneConverter):
    def __init__(self):
        self.strict = False

    async def convert(self, ctx: commands.Context, arg: str) -> Union[NoneType, discord.Invite]:
        arg = await super().convert(ctx, arg)
        if arg is None:
            return arg
        return await commands.InviteConverter().convert(ctx, arg)


class Route(discord.http.Route):
    BASE = "https://discord.com/api/v8"


async def send_button(ctx: commands.Context, url: str, content: str = None, **kwargs) -> discord.Message:
    """Send with a button!"""
    payload = {}
    state = ctx._state
    if content:
        payload["content"] = str(content)
    emb, embs = kwargs.get("embed"), kwargs.get("embeds")
    if emb and embs:
        raise TypeError("You cannot specify both 'embed' and 'embeds'")
    if emb:
        payload["embeds"] = [emb.to_dict()]
    if embs:
        payload["embeds"] = [e.to_dict() for e in embs]
    payload["components"] = [
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "label": f"Click here to invite {ctx.me.name}",
                    "style": 5,
                    "url": str(url),
                }
            ]
        }
    ]
    if al := kwargs.get("allowed_mentions"):
        if state.allowed_mentions is not None:
            payload["allowed_mentions"] = state.allowed_mentions.merge(al).to_dict()
        else:
            payload["allowed_mentions"] = allowed_mentions.to_dict()
    else:
        payload["allowed_mentions"] = state.allowed_mentions and state.allowed_mentions.to_dict()
    channel = kwargs.get("channel", ctx.channel)
    r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel.id)
    data = await ctx.bot.http.request(r, json=payload)
    return discord.Message(state=state, channel=channel, data=data)

