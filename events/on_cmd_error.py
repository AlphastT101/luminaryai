import discord
import traceback
from discord.ext import commands

error_log_channel_id = 1191754729592717383

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound): return

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=error))
            return

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description="I don't have the necessary permissions to perform this action."))
            return

        command_name = ctx.command.name if ctx.command else "Unknown"
        if command_name == "eval": return

        try: raise error

        except Exception as e:
            line_number = traceback.extract_stack()[-2].lineno
            await self.bot.get_channel(error_log_channel_id).send(embed=discord.Embed(
                title="Ouch! Error!",
                description=f"`{ctx.author} used '{command_name}' command in {ctx.guild.name} at line {line_number}!`\n\n**Error:** ```bash\n{e}```",
                color=discord.Color.red()
            ))

            await ctx.send(embed=discord.Embed(
                description=f"An error occurred while executing the command. Please try again a few moments later.",
                color=discord.Color.red()
            ))

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
