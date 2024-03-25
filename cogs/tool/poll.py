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

#<--------------View-------------->

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
        poll_path = Path(f'data/polls/{self.ctx.guild.id}/{interaction.user.id}/active/{poll_id}.json')
        archive_path = Path(f'data/polls/{self.ctx.guild.id}/{interaction.user.id}/archive/{poll_id}.json')
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

#<--------------Cog-------------->
        
class Polls(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

#<--------------Utility-------------->

    async def save_poll_data(self, guild_id: int, user_id: int, poll_id: str, data: dict, message_id: int):
        """投票データを保存する"""
        active_polls_path = Path(f'data/polls/{guild_id}/{user_id}/active')
        active_polls_path.mkdir(parents=True, exist_ok=True)
        data['message_id'] = message_id
        with open(active_polls_path / f'{poll_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

#<--------------Commands-------------->

    @commands.hybrid_group(name='polls', aliases=['vote'])
    async def polls_group(self, ctx: commands.Context):
        """投票に関するコマンド"""
        await ctx.send("投票に関するサブコマンドを使ってください")

    @polls_group.command(name='poll', aliases=['po'])
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
            embed.set_footer(text="/polls end で終了")
    
        poll_message = await ctx.send(embed=embed)
    
        for index in range(len(choices)):
            emoji = f'{index+1}\N{COMBINING ENCLOSING KEYCAP}'
            await poll_message.add_reaction(emoji)

        await self.save_poll_data(ctx.guild.id, ctx.author.id, poll_id, poll_data, poll_message.id)

    @polls_group.command(name='expoll', aliases=['exclusivepoll'])
    async def exclusive_poll(self, ctx: commands.Context, *, 質問と選択肢: str):
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
            "exclusive": True
        }

        embed = discord.Embed(title=question, color=0x00ff00)
        for index, choice in enumerate(choices, start=1):
            emoji = f'{index}\N{COMBINING ENCLOSING KEYCAP}'
            embed.add_field(name=f"選択肢{index}", value=choice, inline=False)
            embed.set_footer(text="この投票は複数回答不可です。\n/polls end で終了")

        poll_message = await ctx.send(embed=embed)

        for index in range(len(choices)):
            emoji = f'{index+1}\N{COMBINING ENCLOSING KEYCAP}'
            await poll_message.add_reaction(emoji)

        await self.save_poll_data(ctx.guild.id, ctx.author.id, poll_id, poll_data, poll_message.id)


    @polls_group.command(name="end")
    async def end_poll(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        polls_path = Path(f'data/polls/{guild_id}/{ctx.author.id}/active')
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

#<--------------Event Listener-------------->

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if reaction.emoji != payload.emoji.name:
                async for user in reaction.users():
                    if user.id == payload.user_id:
                        await message.remove_reaction(reaction.emoji, user)

async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))