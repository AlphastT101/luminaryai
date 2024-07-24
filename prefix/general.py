import os
import discord
from discord.ext import commands
from PIL import Image
import requests
import io

def general(bot):

    ####################### user #########################
    @bot.command(name='user', aliases=['!user', '/user'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def user(ctx, user_mention: discord.Member = None):

        # If no user mention, use the author
        user_self = ctx.author
        join_date = user_self.joined_at.strftime('%Y-%m-%d %H:%M:%S')
        creation_date = user_self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        author_self = discord.Embed(
            title=f"Username: {user_self}",
            color=0x99ccff
        )
        author_self.add_field(name='Joined the server on', value=f"{join_date}", inline=False)
        author_self.add_field(name='Joined discord on', value=f"{creation_date}", inline=False)
        author_self.add_field(name='UserID', value=f"{ctx.author.id}", inline=False)
        # Open the image from the author's avatar
        with requests.get(ctx.author.avatar.url) as response:
            response.raise_for_status()

            # Open the image from the downloaded content
            with Image.open(io.BytesIO(response.content)) as img:
                img = img.resize((300, 300))  # Adjust the size as needed

                # Save the resized image to a temporary file
                temp_filename = "resized_author_pfp.png"
                img.save(temp_filename, "PNG")

                # Attach the resized image to the embed
                file = discord.File(temp_filename, filename="resized_author_pfp.png")
                author_self.set_image(url="attachment://resized_author_pfp.png")

        await ctx.send(embed=author_self, file=file)

        # Remove the temporary file after sending
        os.remove(temp_filename)

    @bot.command()
    async def status(ctx, member: discord.Member):
        await ctx.send(f"{member.display_name}'s status is {member.status}")