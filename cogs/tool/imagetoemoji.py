from discord.ext import commands
import discord

class EmojiNameModal(discord.ui.Modal):
    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    name = discord.ui.TextInput(label="絵文字の名前", placeholder="ここに絵文字の名前を入力してください...", max_length=32)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction, self.name.value)

class ImageToEmojiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_to_emoji_command = discord.app_commands.ContextMenu(
            name="画像を絵文字に",
            callback=self.prompt_emoji_name,
            type=discord.AppCommandType.message
        )
        self.bot.tree.add_command(self.image_to_emoji_command)

    async def prompt_emoji_name(self, interaction: discord.Interaction, message: discord.Message):
        modal = EmojiNameModal(title="絵文字の名前を入力(ローマ字かアルファベットで記入してください。)", callback=lambda i, n: self.image_to_emoji(i, message, n))
        await interaction.response.send_modal(modal)

    async def image_to_emoji(self, interaction: discord.Interaction, message: discord.Message, emoji_name: str):
        if not message.attachments:
            await interaction.response.send_message("このメッセージには画像が含まれていません。", ephemeral=True)
            return

        attachment = message.attachments[0]
        if not attachment.content_type.startswith('image/'):
            await interaction.response.send_message("この添付ファイルは画像ではありません。", ephemeral=True)
            return

        try:
            emoji = await interaction.guild.create_custom_emoji(name=emoji_name, image=await attachment.read())
            await interaction.response.send_message(f"絵文字「{emoji_name}」を追加しました: <:{emoji.name}:{emoji.id}>", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"絵文字を追加できませんでした: {e}", ephemeral=True)

    def cog_unload(self):
        self.bot.tree.remove_command(self.image_to_emoji_command.name, type=discord.AppCommandType.message)

async def setup(bot):
    await bot.add_cog(ImageToEmojiCog(bot))