from discord.ext import commands
import discord
import subprocess
import difflib
from pathlib import Path
import pathlib

class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
                
    def _get_available_cogs(self):
        folder_name = 'cogs'
        cur = pathlib.Path('.')
        
        available_cogs = []
        for p in cur.glob(f"{folder_name}/**/*.py"):
            if p.stem == "__init__":
                continue
            module_path = p.relative_to(cur).with_suffix('').as_posix().replace('/', '.')
            if module_path.startswith('cogs.'):
                available_cogs.append(module_path)
        print(available_cogs)
        return available_cogs

    def find_closest_match(self, user_input):
        available_cogs = self._get_available_cogs()
        closest_matches = difflib.get_close_matches(user_input, available_cogs)
        return closest_matches[0] if closest_matches else None

    @commands.hybrid_command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, *, cog: str):
        """指定したcogを再読み込みします"""
        closest_match = self.find_closest_match('cogs.' + cog if not cog.startswith('cogs.') else cog)
        await ctx.defer()
        try:
            await self.bot.reload_extension(closest_match if closest_match else cog)
            await self.bot.tree.sync()
            await ctx.reply(f"{closest_match if closest_match else cog}を再読み込みしました")
        except commands.ExtensionNotLoaded:
            msg = f"'{cog}' は読み込まれていません。もしかして: '{closest_match}'?" if closest_match else f"'{cog}' は読み込まれていません。"
            await ctx.reply(msg)
        except commands.ExtensionFailed as e:
            await ctx.reply(f"'{closest_match if closest_match else cog}' の再読み込み中にエラーが発生しました。\n{type(e).__name__}: {e}")

    @commands.hybrid_command(name='list_cogs', with_app_command=True)
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """現在ロードされているcogsをリスト表示します"""
        embed = discord.Embed(title="ロードされているCogsのファイル名", color=discord.Color.blue())
        loaded_cogs = self.bot.cogs
        module_names = [cog_instance.__module__ for cog_instance in loaded_cogs.values()]
        embed.add_field(name="", value='\n'.join(module_names), inline=False)
        await ctx.send(embed=embed)
        return

async def setup(bot):
    await bot.add_cog(ManagementCog(bot))
