import discord
from discord.ext import commands
from datetime import datetime
import pytz

startup_channel_id = 1220428119299719229
startup_guild_id = 825804625093328896

async def startup_send_webhook(bot, guild_id):
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

    embed = discord.Embed(title="起動通知", description="Botが起動しました。", color=discord.Color.green())
    embed.add_field(name="Bot名", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="CogsList", value=", ".join(bot.cogs.keys()), inline=False)
    embed.set_footer(text="Botは正常に起動しました。")

    webhook = await channel.create_webhook(name=webhook_name)
    await webhook.send(embed=embed)

    await webhook.delete()