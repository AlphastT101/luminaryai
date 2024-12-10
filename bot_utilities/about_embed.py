import time
import psutil
import datetime
from discord import Embed

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
    users = sum(guild.member_count for guild in bot.guilds)
    guilds = len(bot.guilds)

    about = Embed(
        title='About LuminaryAI',
        description=(
            "[Site](<https://xet.netlify.app>)\n"
            "[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n"
            "[Support server](<https://discord.com/invite/hmMBe8YyJ4>)\n"
            "[API Playground](http://45.139.50.97:6077)\n"
            "[Terms of Service](<https://luminaryai.netlify.app/tos>)\n"
            "[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n\n"
            "LuminaryAI is your Discord bot powered by artificial intelligence. "
            "It utilizes cutting-edge AI features to enrich your server's experience, providing automated moderation, text filtering, image generation, and more!\n\n"

            f"**Internal Statics**\n* **RAM:** {ram_text}\n* **CPU:** {cpu_text}\n* **AI Engine:** Luminary\n\n"
            f"**Bot Statics**\n* **Users:** {users}\n* **Guilds:** {guilds}\n* **Uptime:** {str(uptime_duration)}"
        ),
        color=0x99ccff
    )
    about.set_image(url="attachment://ai.png")
    return about