import traceback

import discord
from discord.ext import commands

from bot import config
from bot.utils.embeds import create_error_embed


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=create_error_embed(description=str(error)))
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_error_embed(
                    description="I don't have the necessary permissions to perform this action."
                )
            )
            return

        command_name = ctx.command.name if ctx.command else "Unknown"
        if command_name == "eval":
            return

        try:
            raise error
        except Exception as e:
            line_number = traceback.extract_stack()[-2].lineno
            if config.ERROR_LOG_CHANNEL_ID:
                channel = self.bot.get_channel(config.ERROR_LOG_CHANNEL_ID)
                if channel:
                    await channel.send(
                        embed=create_error_embed(
                            title="Ouch! Error!",
                            description=(
                                f"`{ctx.author} used '{command_name}' command in {ctx.guild.name} "
                                f"at line {line_number}!`\n\n**Error:** ```bash\n{e}```"
                            ),
                        )
                    )

            await ctx.send(
                embed=create_error_embed(
                    description="An error occurred while executing the command. Please try again a few moments later."
                )
            )


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
