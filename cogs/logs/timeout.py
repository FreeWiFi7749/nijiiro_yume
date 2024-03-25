import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta, timezone

class TimeoutLoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config_path(self, guild_id):
        config_dir = f"data/logs/{guild_id}/config"
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "timeout.json")

    def load_config(self, guild_id):
        config_path = self.get_config_path(guild_id)
        if not os.path.exists(config_path):
            return {"log_timeout": True, "log_channel": None}
        with open(config_path, 'r') as f:
            return json.load(f)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.communication_disabled_until != after.communication_disabled_until:
            config = self.load_config(after.guild.id)
            if not config.get("log_timeout"):
                return
            
            log_channel_id = config.get("log_channel")
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel is None:
                return

            JST = timezone(timedelta(hours=+9))
            now = datetime.now(JST)
            
            if after.communication_disabled_until:
                embed = discord.Embed(title="ユーザータイムアウト設定ログ", color=discord.Color.orange(), timestamp=now)
                embed.set_author(name=after.display_name, icon_url=after.avatar.url)
                embed.add_field(name="ユーザー名", value=after.display_name + "\n" + after.mention, inline=True)
                embed.add_field(name="ユーザーID", value=str(after.id), inline=True)
                embed.add_field(name="タイムアウト終了時刻", value=after.communication_disabled_until.strftime('%Y/%m/%d %H:%M:%S JST'), inline=True)
            else:
                embed = discord.Embed(title="ユーザータイムアウト解除ログ", color=discord.Color.green(), timestamp=now)
                embed.set_author(name=after.display_name, icon_url=after.avatar.url)
                embed.add_field(name="ユーザー名", value=after.display_name + "\n" + after.mention, inline=True)
                embed.add_field(name="ユーザーID", value=str(after.id), inline=True)

            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TimeoutLoggingCog(bot))