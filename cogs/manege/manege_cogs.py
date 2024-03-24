from discord.ext import commands
import discord
import subprocess
import difflib
from pathlib import Path

class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_available_cogs(self):
        cogs_dir = Path(__file__).parent / 'cogs'
        cog_files = list(cogs_dir.rglob('*.py'))
        
        available_cogs = []
        for cog_file in cog_files:
            relative_path = cog_file.relative_to(cogs_dir.parent)
            module_path = str(relative_path.with_suffix('')).replace('/', '.').replace('\\', '.')
            available_cogs.append(module_path)
        
        return available_cogs

    def find_closest_match(self, user_input):
        closest_matches = difflib.get_close_matches(user_input, self._get_available_cogs())
        return closest_matches[0] if closest_matches else None

    @commands.hybrid_command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, *, cog: str):
        """指定したcogを再読み込みします"""
        try:
            await self.bot.reload_extension(cog)
            await self.bot.tree.sync()
            await ctx.reply(f"{cog}を再読み込みしました")
        except commands.ExtensionNotLoaded:
            closest_match = self.find_closest_match(cog)
            if closest_match:
                msg = f"'{cog}' は読み込まれていません。もしかして: '{closest_match}'?"
            else:
                msg = f"'{cog}' は読み込まれていません。"
            await ctx.reply(msg)
        except commands.ExtensionFailed as e:
            await ctx.reply(f"'{cog}' の再読み込み中にエラーが発生しました。\n{type(e).__name__}: {e}")

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
