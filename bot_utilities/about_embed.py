from discord import Embed
import datetime
import time
import psutil

async def about_embed(start_time, bot):

    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_text = f"{cpu_percent:.0f}% of {cpu_cores} cores"
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    ram_text = f"{ram_percent:.0f}% of {total_ram_gb:.0f}GB ({total_ram_gb * ram_percent / 100:.0f}GB)"
    current_time = time.time()
    difference = int(round(current_time - start_time))
    uptime_duration = datetime.timedelta(seconds=difference)

    about = Embed(
        title='About LuminaryAI',
        description=(
            "[Support server](<https://discord.com/invite/hmMBe8YyJ4>)\n"
            "[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n"
            "[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n"
            "[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n"
            "[Site](<https://luminaryai.netlify.app>)\n"
            "[Terms of Service](<https://luminaryai.netlify.app/tos>)\n\n"
            "LuminaryAI is your Discord bot powered by artificial intelligence. "
            "It utilizes cutting-edge AI features to enrich your server's experience, providing automated moderation, text filtering, image generation, and more!"
        ),
        color=0x99ccff
    )
    about.add_field(name='Owner', value="alphast101", inline=True)
    about.add_field(name='Used languages', value="Python 3.11 | discord.py 2.3.2", inline=True)
    about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
    about.add_field(name='AI engine', value="Luminary", inline=True)
    about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
    about.add_field(name='Users', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
    about.add_field(name='RAM usage', value=f"{ram_text}", inline=True)
    about.add_field(name='CPU usage', value=f"{cpu_text}", inline=True)
    about.set_image(url="attachment://ai.png")

    return about