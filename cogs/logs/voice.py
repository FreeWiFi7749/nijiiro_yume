import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta, timezone

class VoiceLoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config_path(self, guild_id):
        config_dir = f"data/logs/{guild_id}/config"
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "voice.json")

    def load_config(self, guild_id):
        config_path = self.get_config_path(guild_id)
        if not os.path.exists(config_path):
            return {"log_voice": True, "log_channel": None}
        with open(config_path, 'r') as f:
            return json.load(f)

    def save_config(self, guild_id, config):
        with open(self.get_config_path(guild_id), 'w') as f:
            json.dump(config, f, indent=4)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        config = self.load_config(guild_id)
        if not config.get("log_voice"):
            return
        
        log_channel_id = config.get("log_channel")
        if not log_channel_id:
            return

        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return
        
        JST = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(JST)
        embed = None

        if before.channel is None and after.channel is not None:
            embed = discord.Embed(title="ボイスチャンネル入室ログ", color=discord.Color.green(), timestamp=now)
            embed.add_field(name="参加したチャンネル", value=f"{after.channel.name}\n{after.channel.mention}", inline=True)
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(title="ボイスチャンネル退出ログ", color=discord.Color.red(), timestamp=now)
            embed.add_field(name="退出したチャンネル", value=f"{before.channel.name}\n{before.channel.mention}", inline=True)
        elif before.channel != after.channel:
            embed = discord.Embed(title="ボイスチャンネル移動ログ", color=discord.Color.blue(), timestamp=now)
            embed.add_field(name="移動前のチャンネル", value=f"{before.channel.name}\n{before.channel.mention}", inline=True)
            embed.add_field(name="移動後のチャンネル", value=f"{after.channel.name}\n{after.channel.mention}", inline=True)

        if embed:
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            embed.set_footer(text=member.guild.name, icon_url=member.guild.icon.url)
            embed.add_field(name="ユーザー", value=member.mention, inline=True)

            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                return

async def setup(bot):
    await bot.add_cog(VoiceLoggingCog(bot))