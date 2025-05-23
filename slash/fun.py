import os
import random
import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone
from bot_utilities.fun_utils import *
from bot_utilities.owner_utils import *
from discord import app_commands, Interaction


class FunSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="randomfact", description="Shows a random fact.")
    @app_commands.guild_only()
    async def randomfact(self, interaction: Interaction):
        if await check_blist(interaction, self.bot.db): return
        random_fact_embed = discord.Embed(
            title="Here is your random fact!",
            description=random.choice(facts),
            color=0x0000ff
        )
        await interaction.response.send_message(embed=random_fact_embed)

    @app_commands.command(name='rps', description="Play RPS with the bot")
    @app_commands.guild_only()
    @app_commands.describe(user_choice="Choose your move")
    @app_commands.choices(user_choice=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors")
    ])
    async def rps(self, interaction: Interaction, user_choice: str):
        if await check_blist(interaction, self.bot.db): return

        bot_choice = random.choice(choices)
        outcome = outcomes[user_choice.lower()][bot_choice]
        await interaction.response.send_message(f"**You choose `{user_choice}`**.\n**I choose `{bot_choice}`.**\n**You `{outcome}`!**")

    @app_commands.command(name="wordle", description="Play wordle!")
    @commands.guild_only()
    async def wordle(self, interaction: Interaction):
        if await check_blist(interaction, self.bot.db): return
        await interaction.response.defer(ephemeral=False)
        word = random.choice(words_list)
        now =  datetime.now(timezone.utc)

        game_start = discord.Embed(
            color=discord.Color.green(),
            description=f"**Welcome to Wordle! Try to guess this 5-letter word in 5 guesses. You have 60 seconds to complete this game.**"
        )
        game_start.timestamp = now

        await interaction.followup.send(embed=game_start)
        
        cache_dir = os.path.join(os.getcwd(), 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        for i in range(5):
            try:
                user_input = await self.bot.wait_for("message", timeout=60, check=lambda message: message.author == interaction.user)
            except asyncio.TimeoutError:
                return await interaction.followup.send(embed=discord.Embed(description=f"**You took too long to respond. Game over! The word was {word}**", color=discord.Color.green()))
            
            user_guess = user_input.content.lower()

            if len(user_guess) == 5 and ' ' not in user_guess and user_guess.isalpha():
                colors = wordleScore(word, user_guess)
                colors_str = [str(color) for color in colors]
                image = generate_wordle_image(user_guess, colors_str)
                image_path = os.path.join(cache_dir, f"wordle_{interaction.user.id}.png")
                image.save(image_path)

                with open(image_path, "rb") as file:
                    discord_file = discord.File(file)
                    await interaction.followup.send(file=discord_file)

                if user_guess == word:
                    return await interaction.followup.send(embed=discord.Embed(description="Congratulations! You guessed the word!", color=discord.Color.green()))

            else:
                await interaction.followup.send(embed=discord.Embed(description="Invalid input. Your guess should be exactly 5 letters.", color=discord.Color.red()))
                continue

        await interaction.followup.send(embed=discord.Embed(description=f"Out of guesses. The word was: {word}", color=discord.Color.green()))

async def setup(bot):
    await bot.add_cog(FunSlash(bot))