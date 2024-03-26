import discord
from discord.ext import commands
import os
import json

class ReplyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_folder = "data/reply/"
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

#<------Event Handler------>

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
    
        if str(payload.emoji) == '💬':
            guild_id = str(payload.guild_id)
            channel_id = str(payload.channel_id)
            if self.is_enabled_for_channel(guild_id, channel_id):
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                if message.author.bot:
                    return
                await channel.create_thread(name=f"{message.author}へのリプライ", message=message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        user_id = str(message.author.id)
        if self.is_enabled_for_channel(guild_id, channel_id) and self.is_user_enabled(guild_id, channel_id, user_id):
            await message.add_reaction('💬')

#<------Commands------>

    @commands.hybrid_group()
    async def reply(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("サブコマンドが無効です...")

    @reply.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def reply_add(self, ctx, channel: discord.TextChannel):
        """リプライ機能を追加します。"""
        self.set_channel_config(ctx.guild.id, channel.id, True)
        await ctx.send(f"{channel.mention} にリプライ機能を追加しました。")

    @reply.command(name="rm")
    @commands.has_permissions(manage_channels=True)
    async def reply_remove(self, ctx, channel: discord.TextChannel):
        """リプライ機能を削除します。"""
        self.set_channel_config(ctx.guild.id, channel.id, False)
        await ctx.send(f"{channel.mention} のリプライ機能を削除しました。")

    @reply.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def reply_list(self, ctx):
        """リプライ機能が有効になっているチャンネルを表示します。"""
        guild_id = str(ctx.guild.id)
        config_folder = os.path.join(self.config_folder, guild_id)
        if os.path.exists(config_folder):
            channels = os.listdir(config_folder)
            if channels:
                message = "リプライが有効になっているチャンネル\n"
                for channel_id in channels:
                    config_path = os.path.join(config_folder, channel_id, "config.json")
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        if config.get("enabled"):
                            channel = self.bot.get_channel(int(channel_id))
                            if channel:
                                message += f"- {channel.mention}\n"
                if message == "リプライが有効になっているチャンネル\n":
                    await ctx.send("リプライ機能が有効になっているチャンネルはありません。")
                else:
                    await ctx.send(message)
            else:
                await ctx.send("リプライ機能が有効になっているチャンネルはありません。")
        else:
            await ctx.send("リプライ機能が有効になっているチャンネルはありません。")

    @commands.hybrid_group(name="リプライ")
    async def reply_user(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("サブコマンドが無効です...")

    @reply_user.command(name="オン")
    async def reply_on(self, ctx):
        """このチャンネルでのメッセージに対するリプライ機能を有効にします。"""
        self.set_user_config(ctx.guild.id, ctx.channel.id, ctx.author.id, True)
        await ctx.send("このチャンネルでのメッセージに対するリプライ機能が有効になりました。", ephemeral=True)

    @reply_user.command(name="オフ")
    async def reply_off(self, ctx):
        """このチャンネルでのメッセージに対するリプライ機能を無効にします。"""
        self.set_user_config(ctx.guild.id, ctx.channel.id, ctx.author.id, False)
        await ctx.send("このチャンネルでのメッセージに対するリプライ機能が無効になりました。", ephemeral=True)

#<------Config------>

    def is_enabled_for_channel(self, guild_id, channel_id):
        config_path = os.path.join(self.config_folder, f"{guild_id}/{channel_id}/config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get("enabled", False)
        return False

    def set_channel_config(self, guild_id, channel_id, enabled):
        config_folder = os.path.join(self.config_folder, f"{guild_id}/{channel_id}")
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        config_path = os.path.join(config_folder, "config.json")
        with open(config_path, 'w') as f:
            json.dump({"enabled": enabled}, f)

    def set_user_config(self, guild_id, channel_id, user_id, enabled):
        config_folder = os.path.join(self.config_folder, f"{guild_id}/{channel_id}/user")
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        config_path = os.path.join(config_folder, f"{user_id}.json")
        with open(config_path, 'w') as f:
            json.dump({"enabled": enabled}, f)

    def is_user_enabled(self, guild_id, channel_id, user_id):
        config_path = os.path.join(self.config_folder, f"{guild_id}/{channel_id}/user/{user_id}.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get("enabled", False)
        return False

async def setup(bot):
    await bot.add_cog(ReplyCog(bot))