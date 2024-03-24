import discord
from discord.ext import commands

from utils.auto_reaction import save_reaction_config, remove_reaction_config, load_reaction_config

class AutoReactionCog(commands.Cog, name='auto reaction'):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        config = load_reaction_config(str(message.guild.id), str(message.channel.id))
        if config and 'emojis' in config:
            for emoji in config['emojis']:
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    continue


    @commands.hybrid_group(name='auto_reaction', invoke_without_command=True)
    async def auto_reaction_group(self, ctx):
        """自動リアクションのグループコマンド"""
        await ctx.send("自動リアクションのサブコマンドを使ってください")

    @auto_reaction_group.command(name='set')
    async def set(self, ctx, channel: discord.TextChannel, emoji: str):
        """指定したチャンネルに自動リアクションを設定します"""
        save_reaction_config(str(ctx.guild.id), str(channel.id), emoji)
        await ctx.send(f"{channel.mention}に送信されたメッセージに{emoji}をリアクションします")

    @auto_reaction_group.command(name='remove')
    async def remove(self, ctx, channel: discord.TextChannel, emoji: str = None):
        """指定したチャンネルから特定の自動リアクションを削除します。絵文字が指定されない場合は、すべての自動リアクションを削除します。"""
        if emoji:
            removed = remove_reaction_config(str(ctx.guild.id), str(channel.id), emoji)
            if removed:
                await ctx.send(f"{channel.mention}から自動リアクション {emoji} を削除しました")
            else:
                await ctx.send(f"{channel.mention} に {emoji} の自動リアクションが見つかりませんでした")
        else:
            remove_reaction_config(str(ctx.guild.id), str(channel.id))
            await ctx.send(f"{channel.mention}からすべての自動リアクションを削除しました")
        
    @auto_reaction_group.command(name='list')
    async def list(self, ctx, channel: discord.TextChannel):
        """指定したチャンネルの自動リアクションを表示します"""
        config = load_reaction_config(str(ctx.guild.id), str(channel.id))
        if config is not None and 'emojis' in config:
            emojis_list = ", ".join(config['emojis'])
            await ctx.send(f"{channel.mention}の自動リアクション: {emojis_list}")
        else:
            await ctx.send(f"{channel.mention}には自動リアクションが設定されていません")

async def setup(bot):
    await bot.add_cog(AutoReactionCog(bot))