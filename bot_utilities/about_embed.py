async def about_embed(start_time, bot):

    cpu_percent = bot.modules_psutil.cpu_percent(interval=1)
    ram_percent = bot.modules_psutil.virtual_memory().percent
    cpu_cores = bot.modules_psutil.cpu_count(logical=True)
    cpu_text = f"{cpu_percent:.0f}% of {cpu_cores} cores"
    total_ram_gb = bot.modules_psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    ram_text = f"{ram_percent:.0f}% of {total_ram_gb:.0f}GB ({total_ram_gb * ram_percent / 100:.0f}GB)"
    current_time = bot.modules_time.time()
    difference = int(round(current_time - start_time))
    uptime_duration = bot.modules_datetime.timedelta(seconds=difference)
    users = sum(guild.member_count for guild in bot.guilds)
    guilds = len(bot.guilds)

    about = bot.modules_discord.Embed(
        title='About LuminaryAI',
        description=(
            "[Site](<https://xet.one>)\n"
            "[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n"
            "[Support server](<https://discord.com/invite/hmMBe8YyJ4>)\n"
            "[API Playground](<https://play.xet.one>)\n"
            "[Terms of Service](<https://xet.one>)\n"
            "[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n\n"
            "LuminaryAI is your Discord bot powered by artificial intelligence, by XET. "
            "It utilizes cutting-edge AI features to enrich your server's experience, providing automated moderation, text filtering, image generation, and more!\n\n"

            f"**Internal Statics**\n* **RAM:** {ram_text}\n* **CPU:** {cpu_text}\n* **AI Engine:** Luminary\n\n"
            f"**Bot Statics**\n* **Users:** {users}\n* **Guilds:** {guilds}\n* **Uptime:** {str(uptime_duration)}"
        ),
        color=0x99ccff
    )
    about.set_image(url="attachment://ai.png")
    return about