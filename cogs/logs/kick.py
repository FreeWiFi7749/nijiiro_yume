import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone, timedelta

class KickLoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config_path(self, guild_id):
        config_dir = f"data/logs/{guild_id}/config"
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "kick.json")

    def load_config(self, guild_id):
        config_path = self.get_config_path(guild_id)
        if not os.path.exists(config_path):
            return {"log_kick": True, "log_channel": None}
        with open(config_path, 'r') as f:
            return json.load(f)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = self.load_config(member.guild.id)
        if not config.get("log_kick"):
            return
        
        log_channel_id = config.get("log_channel")
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel is None:
            return

        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                JST = timezone(timedelta(hours=+9))
                now = datetime.now(JST)
                
                embed = discord.Embed(title="ユーザーキックログ", color=discord.Color.orange(), timestamp=now)
                embed.set_author(name=member.display_name, icon_url=member.avatar.url)
                embed.add_field(name="ユーザー名", value=member.display_name + "\n" + member.mention, inline=True)
                embed.add_field(name="ユーザーID", value=str(member.id), inline=True)
                embed.add_field(name="実行者", value=entry.user.mention, inline=True)
                embed.add_field(name="理由", value=entry.reason or "理由なし", inline=True)
                
                await log_channel.send(embed=embed)
                break

async def setup(bot):
    await bot.add_cog(KickLoggingCog(bot))