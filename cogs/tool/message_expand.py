import discord
from discord.ext import commands
from discord.ui import Button, View
import re

class ImageButtonsView(View):
    def __init__(self, image_urls, author):
        super().__init__(timeout=None)
        self.image_urls = image_urls
        self.author_id = author.id

    @discord.ui.button(label="画像を表示", style=discord.ButtonStyle.primary)
    async def show_images(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.image_urls)
        await interaction.response.defer(ephemeral=True)
        paginator_view = ImagePaginatorView(self.image_urls, self.author_id)
        self.msg = await interaction.followup.send(embed=paginator_view.embed, view=paginator_view, ephemeral=True)
        print("画像を表示ボタンが押されました")
        print(self.msg.id)

class ImagePaginatorView(View):
    def __init__(self, image_urls, author_id):
        super().__init__()
        self.image_urls = image_urls
        self.author_id = author_id
        self.current_index = 0
        self.embed = discord.Embed()
        self.embed.set_image(url=self.image_urls[self.current_index])
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        self.add_item(Button(style=discord.ButtonStyle.secondary, label="◀", disabled=self.current_index == 0, custom_id="left"))
        self.add_item(Button(style=discord.ButtonStyle.secondary, label="▶", disabled=self.current_index == len(self.image_urls) - 1, custom_id="right"))

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary, custom_id="left")
    async def left_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index = max(0, self.current_index - 1)
        self.embed.set_image(url=self.image_urls[self.current_index])
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary, custom_id="right")
    async def right_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index = min(len(self.image_urls) - 1, self.current_index + 1)
        self.embed.set_image(url=self.image_urls[self.current_index])
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

class MessageExpandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enable_link_preview = True

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enable_link_preview or message.author.bot:
            return
        
        discord_link_pattern = re.compile(r'https://discord\.com/channels/(\d+)/(\d+)/(\d+)')
        found_links = discord_link_pattern.findall(message.content)

        for link in found_links:
            if len(link) != 3:
                continue

            guild_id, channel_id, message_id = map(int, link)
            try:
                guild = self.bot.get_guild(guild_id)
                if guild is None:
                    return

                channel = guild.get_channel(channel_id)
                if channel is None:
                    return

                fetched_message = await channel.fetch_message(message_id)
                if fetched_message is None:
                    continue

                if fetched_message.attachments:
                    view = ImageButtonsView([attachment.url for attachment in fetched_message.attachments], message.author)
                    embed = discord.Embed(
                        description=fetched_message.content,
                        timestamp=fetched_message.created_at
                        )
                    embed.set_author(name=fetched_message.author.display_name, icon_url=fetched_message.author.display_avatar.url)
                    #embed.set_author(name=f"{fetched_message.author.display_name}", icon_url=fetched_message.author.display_avatar.url)
                    embed.set_footer(text=f"{fetched_message.guild.name} | {fetched_message.channel.name}\n🗑️で埋め込み消去", icon_url=fetched_message.guild.icon.url)
                    #embed.set_footer(text=f"{fetched_message.guild.name} | {fetched_message.channel.name}",icon_url=fetched_message.guild.icon.url)
                    if fetched_message.attachments:
                        embed.set_image(url=fetched_message.attachments[0].url)
                    
                    embed_message = await message.reply(embed=embed, view=view, mention_author=False)
                    await embed_message.add_reaction("🗑️")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not self.enable_link_preview:
            return

        if str(reaction.emoji) == "🗑️":
            embed = reaction.message.embeds[0] if reaction.message.embeds else None
            if embed and embed.author.name:
                author_text = embed.author.name
                sender_id_str = author_text.split(': ')[-1]
                sender_id = int(sender_id_str)

                if sender_id == user.id:
                    await reaction.message.delete()
                else:
                    await reaction.remove(user)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        print(f"Received interaction: {interaction.data}")

    @commands.hybrid_command(name='message_expand')
    @commands.has_permissions(administrator=True)
    async def toggle_link_preview(self, ctx):
        """リンク展開をオン・オフします。"""
        self.enable_link_preview = not self.enable_link_preview
        state = "有効" if self.enable_link_preview else "無効"
        await ctx.send(f"リンク展開機能が{state}になりました。")

async def setup(bot):
    await bot.add_cog(MessageExpandCog(bot))