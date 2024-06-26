import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta, timezone
import pytz

class RoleLoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config_path(self, guild_id):
        config_dir = f"data/logs/{guild_id}/config"
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "role.json")

    def load_config(self, guild_id):
        config_path = self.get_config_path(guild_id)
        if not os.path.exists(config_path):
            return {"log_roles": True, "log_channel": None}
        with open(config_path, 'r') as f:
            return json.load(f)

    def save_config(self, guild_id, config):
        with open(self.get_config_path(guild_id), 'w') as f:
            json.dump(config, f, indent=4)

    async def _log_role_change(self, guild_id, embed):
        config = self.load_config(guild_id)
        if not config.get("log_roles", True):
            print("Role logging is disabled.")
            return

        log_channel_id = config.get("log_channel")
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        new_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        guild_id = before.guild.id

        JST = timezone(timedelta(hours=+9))
        now = datetime.now(JST)

        if new_roles or removed_roles:
            embed = discord.Embed(title=f"{after.display_name} のロール変更", timestamp=now)
            embed.set_thumbnail(url=after.avatar.url)
            embed.set_author(name=after.display_name, icon_url=after.avatar.url)
            embed.set_footer(text=before.guild.name, icon_url=before.guild.icon.url)
        
            if new_roles:
                added_roles_text = "\n".join(f"✅ {role.mention}" for role in new_roles)
                embed.add_field(name="追加されたロール", value=added_roles_text, inline=False)
        
            if removed_roles:
                removed_roles_text = "\n".join(f"❌ {role.mention}" for role in removed_roles)
                embed.add_field(name="削除されたロール", value=removed_roles_text, inline=False)
        
            await self._log_role_change(guild_id,embed=embed)

async def setup(bot):
    await bot.add_cog(RoleLoggingCog(bot))