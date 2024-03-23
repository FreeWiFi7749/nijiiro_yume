import discord
from discord.ext import commands
import os
import platform
import psutil
import datetime

def create_usage_bar(usage, length=20):
    """使用率に基づいて視覚的なバーを生成する"""
    filled_length = int(length * usage // 100)
    bar = '█' * filled_length + '─' * (length - filled_length)
    return f"[{bar}] {usage}%"

class BotInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def about(self, ctx):
        """Botに関する情報を表示します"""
        

        os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
        cpu_info = platform.processor()
        cpu_cores = f"論理コア: {psutil.cpu_count(logical=True)}, 物理コア: {psutil.cpu_count(logical=False)}"
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')

        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        cpu_bar = create_usage_bar(cpu_usage)
        memory_bar = create_usage_bar(memory_usage)

        embed = discord.Embed(title="サーバー情報", color=0x00ff00)
        embed.add_field(name="所有者", value=f"開発者: <@707320830387814531>\n所有者: Rainbow Server：雑談・通話・ゲーム総合Discord", inline=False)
        embed.add_field(name="OS", value=os_info, inline=False)
        embed.add_field(name="CPU", value=cpu_info, inline=False)
        embed.add_field(name="CPU コア", value=cpu_cores, inline=False)
        embed.add_field(name="起動時間", value=boot_time, inline=False)
        embed.add_field(name="CPU 使用率", value=cpu_bar, inline=False)
        embed.add_field(name="メモリ使用率", value=memory_bar, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfoCog(bot))