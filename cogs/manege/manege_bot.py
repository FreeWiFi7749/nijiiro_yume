import discord
from discord.ext import commands
import sys
import subprocess
import platform
import asyncio

class ManagementBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def rstart_bot(self):
        try:
            if platform.system() == "Linux":
                subprocess.Popen(["sudo", "systemctl", "restart", "nijiiro_yume.service"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["/bin/sh", "-c", "sleep 1; exec python3 " + " ".join(sys.argv)])
            else:
                print("このOSはサポートされていません。")
                return
            await self.bot.close()
        except Exception as e:
            print(f"再起動中にエラーが発生しました: {e}")


    @commands.hybrid_command(name='restart', hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        """Botを再起動する"""
        msg = await ctx.send('10秒後にBotを再起動します')
        for i in range(9, 0, -1):
            await asyncio.sleep(1)
            await msg.edit(content=f"{i}秒後にBotを再起動します")
            if i == 1:
                await msg.edit(content="Botの再起動を開始します...")
                
        await self.rstart_bot()
    
    @commands.hybrid_command(name='shutdown', with_app_command=True, hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Botをシャットダウンする"""
        await ctx.send('Botをシャットダウンします...')
        await self.bot.close()

    @commands.hybrid_command(name='help', with_app_command=True)
    async def list_commands(self, ctx):
        """利用可能なコマンドのリストを教えます"""
        embed = discord.Embed(
            title="コマンドリスト",
            description="利用可能な全てのコマンド",
            color=0xFF8FDF
            )
        
        for command in self.bot.commands:
            if not command.hidden:
                embed.add_field(name=command.name, value=f"説明: {command.help}" or "説明: なし", inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='ping', hidden=True)
    async def ping(self, ctx):
        """BotのPingを表示します"""
        e = discord.Embed(title="Pong!", color=0xFF8FDF)
        e.add_field(name="API Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        e.add_field(name="WebSocket Ping", value=f"{round(self.bot.ws.latency * 1000)}ms", inline=True)
        e.add_field(name="Bot Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(ManagementBot(bot))