import discord
from discord.ext import commands

from bot import config
from bot.utils.embeds import create_success_embed


class MemberJoinHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not config.WELCOME_GUILD_ID or member.guild.id != config.WELCOME_GUILD_ID:
            return

        if not config.WELCOME_CHANNEL_ID:
            return

        welcome_channel = self.bot.get_channel(config.WELCOME_CHANNEL_ID)
        if welcome_channel is None:
            print(f"Welcome channel {config.WELCOME_CHANNEL_ID} not found")
            return

        embed = create_success_embed(
            title="Welcome to the Server!",
            description=f"Welcome {member.mention} to **{member.guild.name}**! 🎉",
        )
        embed.add_field(name="Member Count", value=f"#{len(member.guild.members)}", inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        try:
            await welcome_channel.send(embed=embed)
        except discord.Forbidden:
            print(f"No permission to send messages in channel {config.WELCOME_CHANNEL_ID}")
        except Exception as e:
            print(f"Error sending welcome message: {e}")


async def setup(bot):
    await bot.add_cog(MemberJoinHandler(bot))
