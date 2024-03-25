import discord
from discord.ext import commands
import json
import os

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config_path(self, guild_id):
        config_dir = f"data/logs/{guild_id}/config"
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "nickname.json")

    def load_config(self, guild_id):
        config_path = self.get_config_path(guild_id)
        if not os.path.exists(config_path):
            return {"log_nickname": True, "log_channel": None}
        with open(config_path, 'r') as f:
            return json.load(f)

    def save_config(self, guild_id, config):
        with open(self.get_config_path(guild_id), 'w') as f:
            json.dump(config, f, indent=4)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild_id = before.guild.id
        config = self.load_config(guild_id)
        if not config.get("log_nickname"):
            return

        log_channel_id = config.get("log_channel")
        if not log_channel_id:
            return

        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return
        
        async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
            if entry.target.id == before.id:
                break

        if before.nick != after.nick:
            if after.nick is None:
                embed = discord.Embed(description=f"{after.display_name}のニックネームが`{before.nick}`から`{after.display_name}`に変更されました", color=discord.Color.orange())
            else:
                embed = discord.Embed(description=f"{after.display_name}のニックネームが{before.nick}から{after.nick}に変更されました", color=discord.Color.orange())
            embed.set_thumbnail(url=after.avatar.url)
            embed.set_author(name=after.display_name, icon_url=after.avatar.url)
            embed.set_footer(text=before.guild.name, icon_url=before.guild.icon.url)

            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Nickname(bot))
