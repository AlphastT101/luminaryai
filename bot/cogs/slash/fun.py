import asyncio
import random
from datetime import datetime, timezone

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from bot import config
from bot.utils.embeds import create_error_embed, create_success_embed, create_embed
from bot.utils.fun import choices, facts, generate_wordle_image, outcomes, wordleScore, words_list


class FunSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="randomfact", description="Shows a random fact.")
    @app_commands.guild_only()
    async def randomfact(self, interaction: Interaction):
        random_fact_embed = create_embed(
            title="Here is your random fact!",
            description=random.choice(facts),
        )
        await interaction.response.send_message(embed=random_fact_embed)

    @app_commands.command(name="rps", description="Play RPS with the bot")
    @app_commands.guild_only()
    @app_commands.describe(user_choice="Choose your move")
    @app_commands.choices(
        user_choice=[
            app_commands.Choice(name="Rock", value="rock"),
            app_commands.Choice(name="Paper", value="paper"),
            app_commands.Choice(name="Scissors", value="scissors"),
        ]
    )
    async def rps(self, interaction: Interaction, user_choice: str):
        bot_choice = random.choice(choices)
        outcome = outcomes[user_choice.lower()][bot_choice]
        await interaction.response.send_message(
            f"**You choose `{user_choice}`**.\n**I choose `{bot_choice}`.**\n**You `{outcome}`!**"
        )

    @app_commands.command(name="wordle", description="Play wordle!")
    @app_commands.guild_only()
    async def wordle(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=False)
        word = random.choice(words_list)
        now = datetime.now(timezone.utc)

        game_start = create_success_embed(
            description="**Welcome to Wordle! Try to guess this 5-letter word in 5 guesses. You have 60 seconds to complete this game.**"
        )
        game_start.timestamp = now
        await interaction.followup.send(embed=game_start)

        cache_dir = config.CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)

        for _ in range(5):
            try:
                user_input = await self.bot.wait_for(
                    "message",
                    timeout=60,
                    check=lambda message: message.author == interaction.user,
                )
            except asyncio.TimeoutError:
                return await interaction.followup.send(
                    embed=create_error_embed(
                        description=f"**You took too long to respond. Game over! The word was {word}**"
                    )
                )

            user_guess = user_input.content.lower()

            if len(user_guess) == 5 and " " not in user_guess and user_guess.isalpha():
                colors = wordleScore(word, user_guess)
                colors_str = [str(color) for color in colors]
                image = generate_wordle_image(user_guess, colors_str)
                image_path = cache_dir / f"wordle_{interaction.user.id}.png"
                image.save(image_path)

                with open(image_path, "rb") as file:
                    discord_file = discord.File(file)
                    await interaction.followup.send(file=discord_file)

                if user_guess == word:
                    return await interaction.followup.send(
                        embed=create_success_embed(description="Congratulations! You guessed the word!")
                    )
            else:
                await interaction.followup.send(
                    embed=create_error_embed(description="Invalid input. Your guess should be exactly 5 letters.")
                )
                continue

        await interaction.followup.send(
            embed=create_success_embed(description=f"Out of guesses. The word was: {word}")
        )


async def setup(bot):
    await bot.add_cog(FunSlash(bot))
