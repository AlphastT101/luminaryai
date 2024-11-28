import discord
from discord.ext import commands
import traceback

error_log_channel_id = 1191754729592717383

def on_cmd_error(bot):
    @bot.event
    async def on_command_error(ctx, error):
        #CommandNotFound
        if isinstance(error, commands.CommandNotFound):
            return  # Return without sending an error message
        
        #CommandOnCooldown
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'**This command is on cooldown, you can use it in `{round(error.retry_after, 2)}s`.**'))
            return  # Return without sending an error message

        #MissingPermissions
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(description="**You don't have the necessary permissions to perform this action.**"))
            return
        

        command_name = ctx.command.name if ctx.command else "Unknown"
        if command_name == "eval":
            return
        
        try:
            raise error
        # Member not found
        except discord.ext.commands.errors.MemberNotFound:
            await ctx.send(embed=discord.Embed(title="Member not found", colour=0xFF0000), delete_after=10)
        except Exception as e:

            line_number = traceback.extract_stack()[-2].lineno
            await ctx.bot.get_channel(error_log_channel_id).send(embed=discord.Embed(title="Ouch! Error!", description=f"`{ctx.author} used '{command_name}' command in {ctx.guild.name} at line {line_number}!`\n\n**Error:** ```bash\n{e}```", color=0xFF0000))

            error_embed = discord.Embed(
                title="LuminaryAI - Error!",
                description=f"An error occurred while executing the '{command_name}' command. Please try again a few moments later.",
                color=0xFF0000
            )
            
            await ctx.send(embed=error_embed)