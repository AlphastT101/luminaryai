import random
import discord
from discord.ext import commands
import os
import asyncio
from bot_utilities.fun_utils import *
from datetime import datetime, timezone


facts = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
    "Cows have best friends and can become stressed when they are separated from them.",
    "Bananas are berries, but strawberries aren't.",
    "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion.",
    "A 'jiffy' is an actual unit of time, equivalent to 1/100th of a second.",
    "The first recorded game of baseball was played in 1846 in Hoboken, New Jersey.",
    "The smell of freshly cut grass is actually a plant distress call.",
    "Humans and giraffes have the same number of neck vertebrae (seven).",
    "A group of flamingos is called a 'flamboyance.'",
    "The dot over the letters 'i' and 'j' is called a tittle.",
    "The longest word without a vowel is 'rhythms.'",
    "The first known contraceptive was crocodile dung, used by ancient Egyptians.",
    "Cows have regional accents.",
    "There are more possible iterations of a game of chess than there are atoms in the known universe.",
    "The average person will spend six months of their life waiting for red lights to turn green.",
    "The world's largest desert is Antarctica.",
    "The 'Waffle House Index' is an informal measure used by FEMA to determine the severity of a storm and the likely scale of assistance required for disaster recovery.",
]


words_list = [
    "Apple", "Bacon", "Carry", "Doggy", "Eleph", "Flame", "Grass", "Happy", "Icing", "Jolly",
    "Kitty", "Lemon", "Mango", "Noble", "Olive", "Pizza", "Queen", "Radar", "Sweet", "Tango",
    "Umbra", "Venom", "Water", "Xenon", "Yacht", "Zebra", "Adept", "Bliss", "Candy", "Dwarf",
    "Eagle", "Fairy", "Gears", "Hatch", "Icily", "Jelly", "Kazoo", "Lunar", "Magic", "Nerdy",
    "Oasis", "Puppy", "Quick", "Rover", "Savvy", "Tiger", "Unity", "Vital", "Waltz", "Xerox",
    "Yield", "Zesty", "Amigo", "Baker", "Cutey", "Daisy", "Evoke", "Fudge", "Giant", "Haven",
    "Inked", "Juicy", "Kiosk", "Lemon", "Mocha", "Nymph", "Olive", "Piano", "Quota", "Rusts",
    "Scone", "Table", "Unity", "Vocal", "Whirl", "Xylan", "Yogis", "Zappy", "Angel", "Beach",
    "Candy", "Disco", "Earth", "Fable", "Globe", "Hasty", "Ivory", "Juice", "Kitty", "Lemon",
    "Mocha", "Nylon", "Omega", "Panda", "Queen", "Ruler", "Sunny", "Table", "Unity", "Velum",
    "Whisk", "Xerox", "Yogis", "Zebra"
]



def fun(bot):
    ############### meme #######################
    @bot.command(name="meme", aliases=['!meme', '/meme'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def meme(ctx):
        meme_folder = "memes"
        meme_files = [file for file in os.listdir(meme_folder) if file.endswith(".png")]
        if meme_files:
            selected_photo_path = os.path.join(meme_folder, random.choice(meme_files))
            with open(selected_photo_path, "rb") as file:
                meme_send = discord.File(file)
                await ctx.reply(file=meme_send)
        else:
            await ctx.reply("An error occurred.")


    ############## cat ######################
    @bot.command(name="cat", aliases=['!cat', '/cat'])
    async def cat(ctx):
        cat_folder = "cat"
        cat_files = [file for file in os.listdir(cat_folder) if file.endswith(".png")]
        if cat_files:
            selected_photo_path = os.path.join(cat_folder, random.choice(cat_files))
            await ctx.reply("An error occurred.", delete_after=5)



    ####### random fact #########
    @bot.command(name="randomfact", aliases=['!randomfact', '/randomfact'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomfact(ctx):
        random_fact_embed = discord.Embed(
            title="Here is your random fact!",
            description=random.choice(facts),
            color=0x0000ff
            )
        await ctx.send(embed=random_fact_embed)


    ############################# RPS ##########################
    # Define a list of choices for the game
    choices = ["rock", "paper", "scissors"]
    # Define a dictionary of outcomes for the game
    outcomes = {
        "rock": {"rock": "tie", "paper": "lose", "scissors": "win"},
        "paper": {"rock": "win", "paper": "tie", "scissors": "lose"},
        "scissors": {"rock": "lose", "paper": "win", "scissors": "tie"}
    }

    # Define a command for the game
    @bot.command()
    async def rps(ctx, user_choice: str = None):
        # Check if the user's choice is provided
        if user_choice is None:
            await ctx.send("Specify your choice! Please choose rock, paper, or scissors.")
            return
        # Check if the user's choice is valid
        if user_choice.lower() not in choices:
            await ctx.send("Invalid choice. Please choose rock, paper, or scissors.")
        # Get the bot's choice randomly
        bot_choice = random.choice(choices)
        # Get the outcome of the game
        outcome = outcomes[user_choice.lower()][bot_choice]
        # Send a message with the result
        await ctx.send(f"**You choose {user_choice}**.\n**I choose {bot_choice}.**\n**You {outcome}!**")




    @bot.command(name="wordle")
    async def wordle(ctx):
        word = random.choice(words_list)

        # Get the current time
        now = datetime.now(timezone.utc)

        game_start = discord.Embed(
            color=discord.Color.green(),
            description=f"**Welcome to Wordle! Try to guess this 5-letter word in 5 guesses. You have 60 seconds to complete this game.**"
        )
        game_start.timestamp = now

        await ctx.send(embed=game_start)
        
        for i in range(5):
            
            try:
                user_input = await bot.wait_for("message", timeout=60, check=lambda message: message.author == ctx.author)
            
            except asyncio.TimeoutError:
                return await ctx.send(embed=discord.Embed(description=f"**You took too long to respond. Game over! The word was {word}**", color=discord.Color.green()))
            
            
            user_guess = user_input.content.lower()

            if len(user_guess) == 5 and ' ' not in user_guess and user_guess.isalpha():
                colors = wordleScore(word, user_guess)
                colors_str = [str(color) for color in colors]
                image = generate_wordle_image(user_guess, colors_str)
                image.save(f"wordle_{ctx.author.id}.png")
                with open(f"wordle_{ctx.author.id}.png", "rb") as file:
                    file = discord.File(file)
                    await ctx.send(file=file)
                if user_guess == word:
                    return await ctx.send(embed=discord.Embed(description="Congratulations! You guessed the word!", color=discord.Color.green()))


            else:
                await ctx.send(embed=discord.Embed(description="Invalid input. Your guess should be exactly 5 letters.", color=discord.Color.red()))
                continue
                

        await ctx.send(embed=discord.Embed(description=f"Out of guesses. The word was: {word}", color=discord.Color.green()))