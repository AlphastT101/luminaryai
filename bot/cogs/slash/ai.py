import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.ai import create_and_send_embed, search_image


class AiSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Search the web for images and texts")
    @app_commands.guild_only()
    @app_commands.describe(prompt="Enter prompt for the web to search!")
    async def search(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(ephemeral=False)

        image_urls = await search_image(prompt)
        await create_and_send_embed(prompt, image_urls, None, interaction)


async def setup(bot):
    await bot.add_cog(AiSlash(bot))
