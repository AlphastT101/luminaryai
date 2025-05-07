import os
import random
import discord
import asyncio
from discord.ext import commands
from bot_utilities.fun_utils import *

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="randomfact")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomfact(self, ctx):
        await ctx.reply(embed=discord.Embed(description=random.choice(facts)), mention_author=False)

    @commands.command(name='rps')
    async def rps(self, ctx, user_choice: str = None):

        if user_choice is None or user_choice.lower() not in choices:
            await ctx.reply(embed=discord.Embed(description="Invalid choice, please choose rock, paper, or scissors."), mention_author=False)
            return

        bot_choice = random.choice(choices)
        outcome = outcomes[user_choice.lower()][bot_choice]
        await ctx.reply(embed=discord.Embed(description=f"You choose `{user_choice}`.\nI choose `{bot_choice}`.\nYou **{outcome}!**"), mention_author=False)


    @commands.command(name="wordle")
    async def wordle(self, ctx):
        
        word = random.choice(words_list)
        await ctx.send(embed=discord.Embed(description=f"Welcome to Wordle! Try to guess this 5-letter word in 5 guesses. You have 60 seconds to complete this game."))

        cache_dir = os.path.join(os.getcwd(), 'cache')
        if not os.path.exists(cache_dir): os.makedirs(cache_dir)

        for i in range(5):
            try:
                user_input = await self.bot.wait_for("message", timeout=60, check=lambda message: message.author == ctx.author)
            
            except asyncio.TimeoutError:
                return await ctx.send(embed=discord.Embed(description=f"You took too long to respond. Game over! The word was {word}"))

            user_guess = user_input.content.lower()
            if len(user_guess) == 5 and ' ' not in user_guess and user_guess.isalpha():
                colors = wordleScore(word, user_guess)
                colors_str = [str(color) for color in colors]
                image = generate_wordle_image(user_guess, colors_str)
                image_path = os.path.join(cache_dir, f"wordle_{ctx.author.id}.png")
                image.save(image_path)

                with open(image_path, "rb") as file:
                    discord_file = discord.File(file)
                    await ctx.send(file=discord_file)

                if user_guess == word:
                    return await ctx.send(embed=discord.Embed(description="Congratulations! You guessed the word!", color=discord.Color.green()))

            else:
                await ctx.send(embed=discord.Embed(description="Invalid input. Your guess should be exactly 5 letters.", color=discord.Color.red()))
                continue

        await ctx.send(embed=discord.Embed(description=f"Out of guesses. The word was: {word}", color=discord.Color.green()))

async def setup(bot):
    await bot.add_cog(Fun(bot))