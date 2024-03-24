import discord
from discord.ext import commands
from datetime import datetime
import pytz
import platform
import psutil
from utils.startup_create import create_usage_bar
import os
import pathlib
from pathlib import Path

startup_channel_id = 1220428119299719229
startup_guild_id = 825804625093328896

async def load_cogs(bot, directory='./cogs'):
    failed_cogs = {}
    for path in Path(directory).rglob('*.py'):
        relative_path = path.relative_to('.')
        cog_path = str(relative_path).replace('/', '.').replace('\\', '.')[:-3]

        try:
            await bot.load_extension(cog_path)
        except commands.ExtensionAlreadyLoaded:
            continue
        except Exception as e:
            failed_cogs[cog_path] = str(e)

    return failed_cogs

async def startup_send_webhook(bot, guild_id, startup_channel_id):
    guild = bot.get_guild(guild_id)
    if guild is None:
        print("ギルドが見つかりません。")
        return

    channel = guild.get_channel(startup_channel_id)
    if channel is None:
        print("指定されたチャンネルが見つかりません。")
        return

    jst_time = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d_%H-%M-%S')
    webhook_name = f"{bot.user.name} | {jst_time}"

    failed_cogs = await load_cogs(bot)

    embed = discord.Embed(title="起動通知", description="Botが起動しました。", color=discord.Color.green() if not failed_cogs else discord.Color.red())
    embed.add_field(name="Bot名", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="CogsList", value=", ".join(bot.cogs.keys()), inline=False)
    embed.set_footer(text="Botは正常に起動しました。" if not failed_cogs else "Botは正常に起動していません。")

    if failed_cogs:
        failed_embed = discord.Embed(title="正常に読み込めなかったCogファイル一覧", color=discord.Color.red())
        for cog, error in failed_cogs.items():
            failed_embed.add_field(name=cog, value=error, inline=False)
        webhook = await channel.create_webhook(name=webhook_name)
        await webhook.send(embeds=[embed, failed_embed])
        await webhook.delete()
    else:
        webhook = await channel.create_webhook(name=webhook_name)
        await webhook.send(embed=embed)
        await webhook.delete()

async def startup_send_botinfo(bot):
    guild = bot.get_guild(startup_guild_id)
    if guild is None:
        print("ギルドが見つかりません。")
        return

    channel = guild.get_channel(startup_channel_id)
    if channel is None:
        print("指定されたチャンネルが見つかりません。")
        return
    discord_py_version = discord.__version__
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    cpu_info = platform.processor()
    cpu_cores = f"論理コア: {psutil.cpu_count(logical=True)}, 物理コア: {psutil.cpu_count(logical=False)}"

    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    cpu_bar = create_usage_bar(cpu_usage)
    memory_bar = create_usage_bar(memory_usage)

    embed = discord.Embed(title="BOT情報", color=0x00ff00)
    embed.add_field(name="BOT", value=f"開発者: Rainbow Server開発チーム\n所有権: Rainbow Server：雑談・通話・ゲーム総合Discord", inline=False)
    embed.add_field(name="開発言語", value=f"discord.py {discord_py_version}", inline=False)
    embed.add_field(name="OS", value=os_info, inline=False)
    embed.add_field(name="CPU", value=cpu_info, inline=False)
    embed.add_field(name="CPU コア", value=cpu_cores, inline=False)
    embed.add_field(name="CPU 使用率", value=cpu_bar, inline=False)
    embed.add_field(name="メモリ使用率", value=memory_bar, inline=False)

    webhook = await channel.create_webhook(name="BOT情報")
    await webhook.send(embed=embed)

    await webhook.delete()