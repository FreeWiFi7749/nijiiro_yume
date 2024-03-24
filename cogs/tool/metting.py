import discord
from discord import app_commands
from discord.ext import commands

meeting_form_id = 1220926870334476308

class MeetingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="meeting", description="ミーティング情報を設定する")
    async def meeting(self, interaction: discord.Interaction):
        bot = self.bot

        class MeetingModal(discord.ui.Modal, title="ミーティング情報"):
            def __init__(self, bot, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.bot = bot
                self.add_item(discord.ui.TextInput(label="タイトル", style=discord.TextStyle.short))
                self.add_item(discord.ui.TextInput(label="概要", style=discord.TextStyle.long))
                self.add_item(discord.ui.TextInput(label="メンションロールID", style=discord.TextStyle.short))

            async def on_submit(self, interaction: discord.Interaction):
                print("Inside on_submit")
                await self.callback(interaction)

            async def callback(self, interaction: discord.Interaction):
                print("Inside callback")
                title = self.children[0].value
                description = self.children[1].value
                mention_role_id = self.children[2].value

                forum_channel = self.bot.get_channel(meeting_form_id)
                if isinstance(forum_channel, discord.ForumChannel):
                    thread = await forum_channel.create_thread(
                        name=title,
                        content=f"{description}\n<@&{mention_role_id}>",
                        applied_tags=[]
                    )
                    print("Thread created")
                    await interaction.response.send_message("ミーティング情報がフォーラムチャンネルにスレッドとして投稿されました。", ephemeral=True)

        await interaction.response.send_modal(MeetingModal(bot))

async def setup(bot):
    await bot.add_cog(MeetingCog(bot))