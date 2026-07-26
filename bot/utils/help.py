import discord
from discord.ui import Select

from bot import config

help_select = Select(
    placeholder="Make a selection",
    options=[
        discord.SelectOption(label="Information", emoji="🤖", description="Information commands"),
        discord.SelectOption(label="AI", emoji="✨", description="AI commands"),
        discord.SelectOption(label="Fun", emoji="😂", description="Fun commands"),
        discord.SelectOption(label="Moderation", emoji="🛠️", description="Moderation commands"),
        discord.SelectOption(label="Automod", emoji="⚒️", description="Automod commands"),
        discord.SelectOption(label="Admin", emoji="⚙️", description="Admin commands"),
        discord.SelectOption(label="Music", emoji="🎧", description="Music commands"),
    ],
)

help_embed = discord.Embed(
    title=f"{config.BOT_NAME} - help",
    description=(
        f"[support server](<{config.SUPPORT_SERVER_URL}>)\n"
        f"[Invite bot](<{config.BOT_INVITE_URL}>)\n\n"
        f"{config.BOT_NAME} is like a smart friend on Discord, using a powerful AI engine called 'Luminary' "
        f"made by {config.OWNER_NAME}. It's here to help everyone in the Discord group with anything you need."
    ),
    color=config.EMBED_COLOR_PROCESSING,
)


def get_chunk(embed, commands_list, start, count=5):
    embed.clear_fields()
    for name, value in commands_list[start : start + count]:
        embed.add_field(name=name, value=value, inline=False)

    current_page = (start // count) + 1
    total_pages = (len(commands_list) + count - 1) // count
    prefix = config.BOT_PREFIX
    embed.set_footer(
        text=f"Page {current_page} of {total_pages} | Type {prefix}info <command> for more command information"
    )
    return embed


information_commands = [
    ("`/about`", "❯ About the bot"),
    ("`/help`", "❯ This!"),
    ("`/uptime`", "❯ Bot uptime"),
    ("`/support`", "❯ Support server link"),
    ("`/owner`", "❯ Shows owner of the bot"),
    ("`/ping`", "❯ See bot latency"),
    ("`/userinfo {mention or id}`", "❯ Shows info of a user."),
]

ai_commands = [
    ("`/imagine {prompt}`", "❯ Generate images using SDXL-Turbo"),
    ("`/search {prompt}`", "❯ Search the web for text and images"),
    ("`/api-stats`", "❯ View our API stats"),
]

fun_commands = [
    ("`/rps {your move}`", "❯ Play RPS with the bot"),
    ("`/randomfact`", "❯ Shows a random fact"),
    ("`/wordle`", "❯ Play the wordle game!"),
]

moderation_commands = [
    ("`/purge {number of messages}`", "❯ Purge messages, you need proper permissions to use this command."),
    ("`/ban {user} {reason}`", "❯ Ban a member, you need the ban members permission to take this action."),
    ("`/unban {user} {reason}`", "❯ Unban a member."),
    ("`/kick {user} {reason}`", "❯ Kick a member."),
    ("`/purgefiles {amount of messages}`", "❯ Purge messages that contain files/attachments."),
    ("`/purgelinks {amount of messages}`", "❯ Purge messages that contain links."),
    ("`/unmute {member} {reason}`", "❯ Unmute/remove time out from a member."),
    ("`/timeout {user} {duration} {reason}`", "❯ Timeout a member. A valid time duration required.(eg. 1d,10m,5h)"),
]

automod_commands = []
admin_commands = []

music_commands = [
    (f"`{config.BOT_PREFIX}join`", "❯ Join your voice channel"),
    (f"`{config.BOT_PREFIX}play {{song name}}`", "❯ Play a song from the internet"),
    (f"`{config.BOT_PREFIX}loop`", "❯ Enable loop"),
    (f"`{config.BOT_PREFIX}stop`", "❯ Stop the playback"),
    (f"`{config.BOT_PREFIX}resume`", "❯ Resume the playback"),
    (f"`{config.BOT_PREFIX}pause`", "❯ Pause the playback"),
    (f"`{config.BOT_PREFIX}volume`", "❯ Increase or decrease the volume of the playback."),
    (
        f"`{config.BOT_PREFIX}leave`",
        f"❯ Stop the playback and leave. **Do NOT force {config.BOT_NAME} to leave the voice channel. Just use this command.**",
    ),
]

embed_info = discord.Embed(title="INFORMATION Commands", color=config.EMBED_COLOR_PROCESSING)
embed_ai = discord.Embed(title="AI Commands", color=config.EMBED_COLOR_PROCESSING)
embed_fun = discord.Embed(title="FUN Commands", color=config.EMBED_COLOR_PROCESSING)
embed_moderation = discord.Embed(title="MODERATION Commands", color=config.EMBED_COLOR_PROCESSING)
embed_automod = discord.Embed(title="AUTOMOD Commands - under development", color=config.EMBED_COLOR_PROCESSING)
embed_admin = discord.Embed(title="ADMIN Commands - under development", color=config.EMBED_COLOR_PROCESSING)
embed_music = discord.Embed(title="MUSIC Commands", color=config.EMBED_COLOR_PROCESSING)

embed_info.set_thumbnail(
    url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMqcwdPNaGunh0E1J4YV2O5ch0jbFPL8dw1Q&s"
)
embed_ai.set_thumbnail(
    url="https://th.bing.com/th/id/OIP._C4wM7_FMFicRBck9H6T-QHaHa?w=512&h=512&rs=1&pid=ImgDetMain"
)
embed_fun.set_thumbnail(url="https://i.pinimg.com/736x/9e/80/9a/9e809ad17207f4a040855cd9ebe24713.jpg")
embed_moderation.set_thumbnail(url="https://files.shapes.inc/c11c9c80.png")
embed_music.set_thumbnail(
    url="https://th.bing.com/th/id/OIP.Q96YLM_PXmqQ1EA7P9-zmwHaHa?pid=ImgDet&w=192&h=192&c=7&dpr=1.1"
)
