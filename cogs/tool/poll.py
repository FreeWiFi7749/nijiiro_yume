from discord.ext import commands
import discord
import asyncio
import re
import uuid
import json
from pathlib import Path
from discord.ui import Select, View

def to_emoji(c: int) -> str:
    base = 0x1F1E6
    return chr(base + c)

class PollSelectMenu(Select):
    def __init__(self, polls, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        options = [
            discord.SelectOption(label=poll["question"][:100], description=f"ID: {poll_id}", value=poll_id)
            for poll_id, poll in polls.items()
        ]
        super().__init__(placeholder="終了させたい投票を選択してください...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        poll_id = self.values[0]
        poll_path = Path(f'data/polls/{self.ctx.guild.id}/active/{poll_id}.json')
        archive_path = Path(f'data/polls/{self.ctx.guild.id}/archive/{poll_id}.json')
        if not poll_path.exists():
            await interaction.response.send_message("指定された投票が見つかりません。", ephemeral=True)
            return
        
        with poll_path.open('r', encoding='utf-8') as f:
            poll = json.load(f)
        await interaction.response.defer()
        message_id = poll.get('message_id')
        if not message_id:
            await interaction.response.send_message("メッセージIDが見つかりません。", ephemeral=True)
            return

        try:
            message = await self.ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message("投票メッセージが見つかりません。", ephemeral=True)
            return
        
        results = {}
        for reaction in message.reactions:

            emoji = str(reaction.emoji)
            results[emoji] = reaction.count - 1

        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        result_text = "\n".join([f"{emoji}: {count} 票" for emoji, count in sorted_results])
    
        embed = message.embeds[0]
        embed.add_field(name="投票結果", value=result_text or "結果がありません", inline=False)
        embed.color = discord.Color.red()
        await message.edit(embed=embed)
        await message.clear_reactions()
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        poll_path.rename(archive_path)
        
        await interaction.channel.send("投票が終了しました。")

class PollEndView(View):
    def __init__(self, polls, bot, ctx):
        super().__init__()
        self.add_item(PollSelectMenu(polls, bot, ctx))

class Polls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def save_poll_data(self, guild_id: int, poll_id: str, data: dict, message_id: int):
        """投票データを保存する"""
        path = Path(f'data/polls/{guild_id}/active')
        path.mkdir(parents=True, exist_ok=True)
        data['message_id'] = message_id
        with open(path / f'{poll_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @commands.hybrid_group(name='polls', aliases=['vote'])
    async def polls_group(self, ctx: commands.Context):
        """投票に関するコマンド"""
        await ctx.send("投票に関するサブコマンドを使ってください")


    @polls_group.command(name='poll', aliases=['vote'])
    async def poll(self, ctx: commands.Context, *, 質問: str):
        messages = [ctx.message]
        answers = []

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            instructions_msg = await ctx.send('投票の選択肢を送信してください。\n`/送信`で選択肢の追加を終了し、送信します。')
            messages.append(instructions_msg)

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.send('タイムアウトしました。投票を開始します。')
                break

            if entry.clean_content.startswith('/送信'):
                await entry.delete()
                break

            answers.append((to_emoji(i), entry.clean_content))
            messages.append(entry)

        await ctx.channel.delete_messages(messages)

        poll_id = str(uuid.uuid4())

        poll_data = {
            "question": 質問,
            "answers": answers,
            "author": ctx.author.id,
        }

        embed = discord.Embed(title=質問, color=0x00ff00)
        for emoji, answer in answers:
            embed.add_field(name=emoji, value=answer, inline=False)
    
        actual_poll = await ctx.send(embed=embed)

        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

        await self.save_poll_data(ctx.guild.id, poll_id, poll_data, actual_poll.id)

    @polls_group.command(name='quickpoll', aliases=['qp'])
    async def quickpoll(self, ctx: commands.Context, *, 質問と選択肢: str):
        args = re.split(r'[ 　]+', 質問と選択肢)

        if len(args) < 3:
            return await ctx.send('質問と最低2つの選択肢を入力してください。')

        question = args[0]
        choices = args[1:]
    
        if len(choices) > 20:
            return await ctx.send('選択肢は最大20個までです。')

        poll_id = str(uuid.uuid4())

        poll_data = {
            "question": question,
            "answers": [[f"{index+1}", choice] for index, choice in enumerate(choices)],
            "author": ctx.author.id,
        }

        embed = discord.Embed(title=question, color=0x00ff00)
        for index, choice in enumerate(choices, start=1):
            emoji = f'{index}\N{COMBINING ENCLOSING KEYCAP}'
            embed.add_field(name=f"選択肢{index}", value=choice, inline=False)
    
        poll_message = await ctx.send(embed=embed)
    
        for index in range(len(choices)):
            emoji = f'{index+1}\N{COMBINING ENCLOSING KEYCAP}'
            await poll_message.add_reaction(emoji)

        await self.save_poll_data(ctx.guild.id, poll_id, poll_data, poll_message.id)

    @polls_group.command(name="end")
    async def end_poll(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        polls_path = Path(f'data/polls/{guild_id}/active')
        polls = {}

        if polls_path.exists() and polls_path.is_dir():
            for poll_file in polls_path.iterdir():
                if poll_file.suffix == '.json':
                    with poll_file.open('r', encoding='utf-8') as f:
                        polls[poll_file.stem] = json.load(f)

        if not polls:
            await ctx.send("終了する投票がありません。")
            return

        view = PollEndView(polls, self.bot, ctx)
        await ctx.send("終了させたい投票を選択してください：", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))