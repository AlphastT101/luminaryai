from discord.ext import commands
from bot_utilities.fun_utils import *

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="randomfact")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomfact(self, ctx):
        random_fact_embed = self.bot.modules_discord.Embed(
            title="Here is your random fact!",
            description=self.bot.modules_random.choice(facts),
            color=0x0000ff
            )
        await ctx.send(embed=random_fact_embed)


    @commands.command(name='rps')
    async def rps(self, ctx, user_choice: str = None):

        if user_choice is None:
            await ctx.send("Specify your choice! Please choose rock, paper, or scissors.")
            return
        if user_choice.lower() not in choices:
            await ctx.send("Invalid choice. Please choose rock, paper, or scissors.")

        bot_choice = self.bot.modules_random.choice(choices)
        outcome = outcomes[user_choice.lower()][bot_choice]
        await ctx.send(f"**You choose `{user_choice}`**.\n**I choose `{bot_choice}`.**\n**You `{outcome}`!**")


    @commands.command(name="wordle")
    async def wordle(self, ctx):
        word = self.bot.modules_random.choice(words_list)
        now = self.bot.modules_datetime.datetime.now(self.bot.modules_datetime.timezone.utc)

        game_start = self.bot.modules_discord.Embed(
            color=self.bot.modules_discord.Color.green(),
            description=f"**Welcome to Wordle! Try to guess this 5-letter word in 5 guesses. You have 60 seconds to complete this game.**"
        )
        game_start.timestamp = now
        await ctx.send(embed=game_start)
        cache_dir = self.bot.modules_os.path.join(self.bot.modules_os.getcwd(), 'cache')
        if not self.bot.modules_os.path.exists(cache_dir):
            self.bot.modules_os.makedirs(cache_dir)

        for i in range(5):
            try:
                user_input = await self.bot.wait_for("message", timeout=60, check=lambda message: message.author == ctx.author)
            
            except self.bot.modules_asyncio.TimeoutError:
                return await ctx.send(embed=self.bot.modules_discord.Embed(description=f"**You took too long to respond. Game over! The word was {word}**", color=self.bot.modules_discord.Color.green()))
               
            user_guess = user_input.content.lower()
            if len(user_guess) == 5 and ' ' not in user_guess and user_guess.isalpha():
                colors = wordleScore(word, user_guess)
                colors_str = [str(color) for color in colors]
                image = generate_wordle_image(user_guess, colors_str)
                image_path = self.bot.modules_os.path.join(cache_dir, f"wordle_{ctx.author.id}.png")
                image.save(image_path)

                with open(image_path, "rb") as file:
                    discord_file = self.bot.modules_discord.File(file)
                    await ctx.send(file=discord_file)

                if user_guess == word:
                    return await ctx.send(embed=self.bot.modules_discord.Embed(description="Congratulations! You guessed the word!", color=self.bot.modules_discord.Color.green()))

            else:
                await ctx.send(embed=self.bot.modules_discord.Embed(description="Invalid input. Your guess should be exactly 5 letters.", color=self.bot.modules_discord.Color.red()))
                continue
        await ctx.send(embed=self.bot.modules_vdiscord.Embed(description=f"Out of guesses. The word was: {word}", color=self.bot.modules_discord.Color.green()))

async def setup(bot):
    await bot.add_cog(Fun(bot))