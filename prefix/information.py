import discord
from discord.ext import commands

def information(bot):

    ####################### user #########################
    @bot.command(name='userinfo')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user(ctx, user_mention: discord.Member = None):

        if user_mention is None:
            user_mention = ctx.author

        roles = [role.mention for role in user_mention.roles if role != ctx.guild.default_role]
        roles_string = ", ".join(roles) if roles else "No roles"

        permissions = ctx.channel.permissions_for(user_mention)
        permissions_string = ", ".join([perm.replace('_', ' ').title() for perm, value in permissions if value])

        embed = discord.Embed(
            title=f"Username: {user_mention}",
            description=(
                f"UserID: `{user_mention.id}`\n"
                f"Joined the server: <t:{int(user_mention.joined_at.timestamp())}:R>\n"
                f"Joined Discord: <t:{int(user_mention.created_at.timestamp())}:R>\n\n"
                "**User's Roles:**\n"
                f"{roles_string}\n\n"
                "**Channel Permissions:**\n"
                f"{permissions_string}"
            ),
            color=0x99ccff
        )

        embed.set_thumbnail(url=user_mention.avatar.url)
        await ctx.send(embed=embed)

    @bot.command(name='support')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def support(ctx):
        await ctx.send("> **Support server invite link:** [here](https://discord.com/invite/hmMBe8YyJ4)")

    @bot.command(name='owner')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def owner(ctx):
        await ctx.send("> **My owner is:** [AlphasT101](https://alphast101.netlify.app)")