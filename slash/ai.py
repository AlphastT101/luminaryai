import discord
from discord import app_commands
from discord.ext import commands

class AiSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="imagine", description="Imagine an image using LuminaryAI")
    @app_commands.guild_only()
    @app_commands.describe(
        prompt="Enter the prompt for the image to generate.",
        model="Select the model to use.",
        size="Select the size for the model.")
    @app_commands.choices(model=[
        app_commands.Choice(name="Flux-Dev", value="flux-dev"),
        app_commands.Choice(name="Flux-Schnell", value="flux-schnell"),
        app_commands.Choice(name="SDXL-Turbo", value="sdxl-turbo"),
        app_commands.Choice(name="Polinations.ai", value="poli")
    ],
    size=[
        app_commands.Choice(name="1024x1024", value="1024x1024"),
        app_commands.Choice(name="1024x576", value="1024x576"),
        app_commands.Choice(name="1024x768" ,value="1024x768"),
        app_commands.Choice(name="512x512" ,value="512x512"),
        app_commands.Choice(name="576x1024" ,value="576x1024"),
        app_commands.Choice(name="768x1024" ,value="768x1024")
    ])
    async def imagine_pla(self, interaction: discord.Interaction, prompt: str, model: app_commands.Choice[str], size: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        if await self.bot.func_checkblist(interaction, self.bot.db): return

        if model.value == "poli" and not size.value == "1024x1024":
            await interaction.followup.send(f"> **Size `{size.value}` is not available for polinations.ai**")
            return

        if self.bot.is_generating.get(interaction.user.id):
            await interaction.followup.send("> **You're already generating an image!**")
            return
        if prompt is None:
            await interaction.followup.send("> **Please enter your prompt.**")
            return

        self.bot.is_generating[interaction.user.id] = True
        req = await interaction.followup.send("> **Please wait while I process your request.**")

        link = await self.bot.func_imgen(model.value, prompt, size.value, self.bot)

        try:
            embed = discord.Embed(
                title="LuminaryAI - Image Generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`",
                color=discord.Color.blue()
            )
            embed.set_footer(icon_url=self.bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            embed.set_image(url=link)
            await req.edit(content="", embed=embed)
            self.bot.is_generating[interaction.user.id] = False
        except Exception as e:
            req.edit(content="> **❌ Ouch! something went wrong.**")


    @app_commands.command(name='poli', description="Generate images using Polinations.ai")
    @app_commands.guild_only()
    @app_commands.describe(prompt="Enter the prompt for the image to generate.")
    async def poli_gen(self, interaction: discord.Interaction, prompt: str):

        await interaction.response.defer(ephemeral=False)
        if await self.bot.func_checkblist(interaction, self.bot.db): return
        delete_msg = await interaction.followup.send("> **⌚Please wait while I process your request.**")

        async with self.bot.modules_aiohttp.ClientSession() as session:
            image = await self.bot.func_poly_imgen(session, prompt, self.bot)
            send_embed = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`.",
                color=0x99ccff,
            )
            send_embed.set_footer(icon_url=self.bot.user.avatar.url, text="Thanks for using LuminaryAI!")
            send_embed.set_image(url=f'attachment://generated_image.png')
            await delete_msg.delete()
            await interaction.followup.send(content="", embed=send_embed, file=discord.File(image, 'generated_image.png'))

    @app_commands.command(name="search", description="Seaech the web for images and texts!")
    @app_commands.guild_only()
    @app_commands.describe(prompt="Enter prompt for the web to search!")
    async def search(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(ephemeral=False)
        if await self.bot.func_checkblist(interaction, self.bot.db): return
        image_urls = self.bot.func_search_img(prompt, self.bot)
        await self.bot.func_cse(discord, prompt, interaction, self.bot, image_urls)


    @app_commands.command(name="generate-api-key", description="Generate an API key for XET")
    @app_commands.guild_only()
    async def create_api(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if await self.bot.func_checkblist(interaction, self.bot.db): return
        await interaction.followup.send("> :x: **Please use the [dashboard](https://xet.one/dashboard) to generate an API key.**")

    @app_commands.command(name="delete-api-key", description="Delete Your API key for XET")
    @app_commands.guild_only()
    async def delete_api(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if await self.bot.func_checkblist(interaction, self.bot.db): return
        await interaction.followup.send("> :x: **Please use the [dashboard](https://xet.one/dashboard) to delete an API key.**")

    @app_commands.command(name="api-stats", description="View our API stats")
    @app_commands.guild_only()
    async def api_stats(self, interaction: discord.Interaction):
        if await self.bot.func_checkblist(interaction, self.bot.db): return
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