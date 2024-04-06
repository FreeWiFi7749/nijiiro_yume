import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai

# 環境変数からAPIキーを読み込む
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

# APIキーを設定
if openai_api_key:
    openai.api_key = openai_api_key
else:
    raise ValueError("No API key provided. Please set the OPENAI_API_KEY environment variable.")

class ChatGPTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_message(self, message):
        """指定されたプロンプトに基づいて文を生成する。"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Rainbow serverのアイドル的存在の虹色夢ちゃんになりきって以下の文を変換してください。また、絵文字を多用してください。"},
                    {"role": "user", "content": message}
                ],
                max_tokens=100,
                temperature=0.7
            )
            generated_text = response.choices[0].message['content'].strip()
            return generated_text
        except Exception as e:
            print(f"文の生成中にエラーが発生しました: {e}")
            return "エラーが発生しました。もう一度試してください。"

    @commands.hybrid_command(name="虹色夢")
    async def chat_gpt(self, ctx, *, message):
        """虹色夢になりきって文を生成します。"""
        msg = await ctx.send("文を生成中です...")
        generated_text = await self.generate_message(message)
        await msg.edit(content="文を生成しました。")
        await ctx.send(generated_text)

async def setup(bot):
    await bot.add_cog(ChatGPTCog(bot))