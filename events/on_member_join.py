from discord.ext import commands
import discord

class MemberJoinHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Only handle joins for the specific server ID
        if member.guild.id != 1144903052717985806:
            return
        
        # Get the welcome channel
        welcome_channel_id = 1144903053904990209
        welcome_channel = self.bot.get_channel(welcome_channel_id)
        
        if welcome_channel is None:
            print(f"Welcome channel {welcome_channel_id} not found")
            return
        
        # Create welcome embed
        embed = discord.Embed(
            title="Welcome to the Server!",
            description=f"Welcome {member.mention} to **{member.guild.name}**! 🎉",
            color=discord.Color.green()
        )
        
        # Add member information
        embed.add_field(name="Member Count", value=f"#{len(member.guild.members)}", inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        
        # Set thumbnail to member's avatar
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        # Send welcome message
        try:
            await welcome_channel.send(embed=embed)
        except discord.Forbidden:
            print(f"No permission to send messages in channel {welcome_channel_id}")
        except Exception as e:
            print(f"Error sending welcome message: {e}")

async def setup(bot):
    await bot.add_cog(MemberJoinHandler(bot))
