import datetime
import time

import psutil

from bot import config
from bot.utils.embeds import create_embed


async def about_embed(start_time, bot):
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_text = f"{cpu_percent:.0f}% of {cpu_cores} cores"
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    ram_text = f"{ram_percent:.0f}% of {total_ram_gb:.0f}GB ({total_ram_gb * ram_percent / 100:.0f}GB)"
    current_time = time.time()
    difference = int(round(current_time - start_time))
    uptime_duration = datetime.timedelta(seconds=difference)
    users = sum(guild.member_count for guild in bot.guilds)
    guilds = len(bot.guilds)

    about = create_embed(
        title=f"About {config.BOT_NAME}",
        description=(
            f"[Site](<{config.WEBSITE_URL}>)\n"
            f"[Invite bot](<{config.BOT_INVITE_URL}>)\n"
            f"[Support server](<{config.SUPPORT_SERVER_URL}>)\n"
            f"{config.BOT_NAME} is your Discord bot powered by artificial intelligence, by LumixCore. "
            "It utilizes cutting-edge AI features to enrich your server's experience, providing automated "
            "moderation, text filtering, image generation, and more!\n\n"
            f"**Internal Statics**\n* **RAM:** {ram_text}\n* **CPU:** {cpu_text}\n* **AI Engine:** Luminary\n\n"
            f"**Bot Statics**\n* **Users:** {users}\n* **Guilds:** {guilds}\n* **Uptime:** {str(uptime_duration)}"
        ),
    )
    about.set_image(url="attachment://ai.png")
    return about
