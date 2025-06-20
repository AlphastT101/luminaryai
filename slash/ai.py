import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from bot_utilities.owner_utils import check_blist
from bot_utilities.ai_utils import poli, search_image, create_and_send_embed, gentext

def is_admin_or_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        if await interaction.client.is_owner(interaction.user):
            return True
        perms = interaction.user.guild_permissions
        return perms.administrator
    return app_commands.check(predicate)

class AiSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # @app_commands.command(name="imagine", description="Imagine an image")
    # @app_commands.guild_only()
    # @app_commands.describe(
    #     prompt="Enter the prompt for the image to generate.",
    #     model="Select the model to use.",
    #     size="Select the size for the model.")
    # @app_commands.choices(model=[
    #     # app_commands.Choice(name="Flux-Dev", value="flux-dev"),
    #     app_commands.Choice(name="Flux-Schnell", value="flux-schnell"),
    #     app_commands.Choice(name="SDXL-Lighting", value="sdxl-lighting"),
    #     app_commands.Choice(name="Polinations.ai", value="poli")
    # ],
    # size=[
    #     app_commands.Choice(name="1024x1024", value="1024x1024"),
    #     app_commands.Choice(name="1024x576", value="1024x576"),
    #     app_commands.Choice(name="1024x768" ,value="1024x768"),
    #     app_commands.Choice(name="512x512" ,value="512x512"),
    #     app_commands.Choice(name="576x1024" ,value="576x1024"),
    #     app_commands.Choice(name="768x1024" ,value="768x1024")
    # ])
    # async def imagine_pla(self, interaction: discord.Interaction, prompt: str, model: app_commands.Choice[str], size: app_commands.Choice[str]):
    #     await interaction.response.defer(ephemeral=False)
    #     if await check_blist(interaction, self.bot.db): return

    #     await interaction.followup.send(embed=discord.Embed(description="We're working on it."))


    @app_commands.command(name='imagine', description="Generate images using SDXL-Turbo")
    @app_commands.guild_only()
    @app_commands.describe(prompt="Enter the prompt for the image to generate.")
    async def poli_gen(self, interaction: discord.Interaction, prompt: str):

        await interaction.response.defer(ephemeral=False)
        if await check_blist(interaction, self.bot.db): return

        async with aiohttp.ClientSession() as session:
            image = await poli(session, prompt)
            send_embed = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`.",
            )
            send_embed.set_image(url=f'attachment://generated_image.png')
            await interaction.followup.send(content="", embed=send_embed, file=discord.File(image, 'generated_image.png'))

    @app_commands.command(name="search", description="Seaech the web for images and texts")
    @app_commands.guild_only()
    @app_commands.describe(prompt="Enter prompt for the web to search!")
    async def search(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(ephemeral=False)
        if await check_blist(interaction, self.bot.db): return
        image_urls = await search_image(prompt)
        await create_and_send_embed(prompt, image_urls, None, interaction)


    @app_commands.command(name="ask", description="Ask the bot a question.")
    @app_commands.guild_only()
    @app_commands.describe(question="what would u ask??")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer(ephemeral=False)
        if await check_blist(interaction, self.bot.db): return

        user_id = interaction.user.id
        if user_id not in self.bot.history: self.bot.history[user_id] = []
        history = self.bot.history[user_id]

        history.append({"role": "user","content": question})
        response = await gentext(history)
        history.append({"role": "assistant","content": response})
        self.bot.history[user_id] = history

        await interaction.followup.send(response)
    
    @app_commands.command(name="activate", description="Activate AI responding to this channel")
    @is_admin_or_owner()
    @app_commands.guild_only()
    async def activate(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if await check_blist(interaction, self.bot.db): return

        collection = self.bot.db['bot']['activated_channels']
        collection.update_one(
            {"id": interaction.channel.id},
            {"$set": {"id": interaction.channel.id}},
            upsert=True
        )
        await interaction.followup.send("Now responding to **all** messages in this channel.")

    @app_commands.command(name="deactivate", description="Deactivate AI responding to this channel")
    @is_admin_or_owner()
    @app_commands.guild_only()
    async def deactivate(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if await check_blist(interaction, self.bot.db): return

        collection = self.bot.db['bot']['activated_channels']
        collection.delete_one({"id": interaction.channel.id})

        await interaction.followup.send("AI has been deactivated.")

    @app_commands.command(name="api-stats", description="View our API stats")
    @app_commands.guild_only()
    async def api_stats(self, interaction: discord.Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)

        db = self.bot.db['lumi-api']
        collection = db['stats']
        stats = collection.find_one({"key": "api_stats"})

        if stats and 'value' in stats:
            model_stats = stats['value']
            formatted_stats = []

            for model_name, total_requests in model_stats.items():
                formatted_stats.append(f"**{model_name}:** `{total_requests}`")

            stats = "\n".join(formatted_stats)
        else:
            stats = "No API stats found."

        embed = discord.Embed(
            title="XET API Stats",
            description=stats,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Current XET API Stats")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AiSlash(bot))