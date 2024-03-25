import discord
import random
import asyncio
from discord.ext import tasks

presences = [
    {"type": "Playing", "name": "/helpでコマンドを確認"},
    {"type": "Playing", "name": "虹色 夢 Ver.0.1.0α"},
    {"type": "Watching", "name": "Rainbow Server：雑談・通話・ゲーム総合Discord"},
]

async def update_presence(bot):
    while not bot.is_closed():
        presence = random.choice(presences)
        activity_type = getattr(discord.ActivityType, presence["type"].lower(), discord.ActivityType.playing)
        await bot.change_presence(activity=discord.Activity(type=activity_type, name=presence["name"]))
        await asyncio.sleep(60)