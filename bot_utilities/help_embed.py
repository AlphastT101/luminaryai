import discord
from discord.ui import Select, View

help_select = Select(placeholder="Make a selection", options=[
    discord.SelectOption(label="Information", emoji="🤖", description="Information commands"),
    discord.SelectOption(label="AI", emoji="✨", description="AI commands"),
    discord.SelectOption(label="Fun", emoji="😂", description="Fun commands"),
    discord.SelectOption(label="Moderation", emoji="🛠️", description="Moderation commands"),
    discord.SelectOption(label="Automod", emoji="⚒️", description="Automod commands"),
    discord.SelectOption(label="Admin", emoji="⚙️", description="Admin commands"),
    discord.SelectOption(label="Music", emoji="🎧", description="Music commands"),
])


help_embbed = discord.Embed(
    title="LuminaryAI - help",
    description="[support server](<https://discord.com/invite/hmMBe8YyJ4>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n\nLuminaryAI is like a smart friend on Discord, using a powerful AI engine called 'Luminary' made by AlphasT101. It's here to help everyone in the Discord group with anything you need.",
    color=0x99ccff  # Convert hex color to integer
)

# Function to get a chunk of commands
def get_chunk(embed, commands_list, start, count=5):
    embed.clear_fields()
    for name, value in commands_list[start:start + count]:
        embed.add_field(name=name, value=value, inline=False)
    current_page = (start // count) + 1
    total_pages = (len(commands_list) + count - 1) // count
    embed.set_footer(text=f"Page {current_page} of {total_pages} | Type ai.info <command> for more command information")
    return embed



information_commannds = [
    ("`/about`", "❯ About the bot"),
    ("`/help`", "❯ Command list"),
    ("`/uptime`", "❯ Bot uptime"),
    ("`/support`", "❯ Support server link"),
    ("`/owner`", "❯ Shows owner of the bot"),
    ("`/userinfo {mention or id}`", "❯ Shows info of a user.")
]

ai_commands = [
    ('`/imagine {prompt}`', "❯ Generates images using Lumage-1."),
    ('`/poli {prompt}`', "❯ Generates images using pollinations.ai according to user-inputs. We prefer to use the slash command `/imagine`"),
    # ('`/ask {prompt}`', "❯ Generates answers according to user-inputs. Message history available"),
    ('`/search {prompt}`', "❯ Search the web for text and images"),
    ('`/vision {prompt}`', "❯ Vision an image. This command is slash only."),
    ('`/generate-api-key`', "❯ Generates an API key for our API, join our support server for more info."),
    ('`/delete-api-key`', "❯ deletes your API key for our API."),
    ('`@luminaryai {prompt}`', "❯ Ping LuminaryAI to generate text and images."),
    ('`@luminaryai activate`', "❯ Enable AI responses, You need admin permissions to run this command."),
    ('`@luminaryai deactivate`', "❯ Disable AI responses. You need admin permissions to run this command.")
]

fun_commands = [
    ('`/rps {your move}`', "❯ Play RPS with the bot"),
    ('`/randomfact`', "❯ Shows a random fact"),
    ('`/wordle`', "❯ Play the wordle game!")
]

moderation_commands = [
    ('`ai.purge {number of messages}`', "❯ Purge messages, you need proper permissions to use this command."),
    ('`ai.ban {user} {reason}`', "❯ Ban a member, you need the ban members permission to take this action."),
    ('`ai.unban {user} {reason}`', "❯ Unban a member."),
    ('`ai.kick {user} {reason}`', "❯ Kick a member."),
    ('`ai.purgefiles {amount of messages}`', "❯ Purge messages that contain files/attachments."),
    ('`ai.purgelinks {amount of messages}`', "❯ Purge messages that contain links."),
    ('`ai.unmute {member} {reason}`', "❯ Unmute/remove time out from a member."),
    ('`ai.timeout {user} {duration} {reason}`', "❯ Timeout a member. A valid time duration required.(eg. 1d,10m,5h)")
]

automod_commands = [
# Placeholder for future commands
]

admin_commands = [
# Placeholder for future commands
]

music_commands = [
    ('`ai.join`', "❯ Join your voice channel"),
    ('`ai.play {song name}`', "❯ Play a song from the internet"),
    ('`ai.loop`', "❯ Enable loop"),
    ('`ai.stop`', "❯ Stop the playback"),
    ('`ai.resume`', "❯ Resume the playback"),
    ('`ai.pause`', "❯ Pause the playback"),
    ('`ai.volume`', "❯ Increase or decrease the volume of the playback."),
    ('`ai.leave`', "❯ Stop the playback and leave. **Do NOT force LuminaryAI to leave the voice channel. Just use this command.**")
]

embed_info = discord.Embed(
    title="INFORMATION COMMANDS",
    color=0x99ccff  # Convert hex color to integer
)

embed_ai = discord.Embed(
    title="AI commands",
    color=0x99ccff  # Convert hex color to integer
)


embed_fun = discord.Embed(
    title="FUN commands",
    color=0x99ccff  # Convert hex color to integer
)

embed_moderation = discord.Embed(
    title="MODERATION commands",
    color=0x99ccff  # Convert hex color to integer
)

embed_automod = discord.Embed(
    title="AUTOMOD commands - under development",
    color=0x99ccff  # Convert hex color to integer
) 

embed_admin = discord.Embed(
    title="ADMIN commands - under development",
    color=0x99ccff  # Convert hex color to integer
)

embed_music = discord.Embed(
    title="MUSIC commands",
    color=0x99ccff  # Convert hex color to integer
)



# Set thumbnails for each embed
bot_thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMqcwdPNaGunh0E1J4YV2O5ch0jbFPL8dw1Q&s"
ai_thumbnail = "https://th.bing.com/th/id/OIP._C4wM7_FMFicRBck9H6T-QHaHa?w=512&h=512&rs=1&pid=ImgDetMain"
fun_thumbnail = "https://i.pinimg.com/736x/9e/80/9a/9e809ad17207f4a040855cd9ebe24713.jpg"
moderation_thumbnail = "https://images-ext-1.discordapp.net/external/BsiRCTyfJ2MTKjvIuabRlcOIGwxZ9G5Ydu-q6nhZ7Hc/https/files.shapes.inc/c11c9c80.png?format=webp&quality=lossless&width=671&height=671"
# automod_thumbnail = "https://img.freepik.com/free-vector/robot-arm-concept-illustration_114360-8436.jpg?size=338&ext=jpg&ga=GA1.1.2008272138.1720483200&semt=sph"
# admin_thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQmO27HNo399ZS89SSJl3DfmfZjUhY-6Bm4Q&s"
music_thumbnail = "https://th.bing.com/th/id/OIP.Q96YLM_PXmqQ1EA7P9-zmwHaHa?pid=ImgDet&w=192&h=192&c=7&dpr=1.1"

embed_info.set_thumbnail(url=bot_thumbnail)
embed_ai.set_thumbnail(url=ai_thumbnail)
embed_fun.set_thumbnail(url=fun_thumbnail)
embed_moderation.set_thumbnail(url=moderation_thumbnail)
embed_music.set_thumbnail(url=music_thumbnail)
# embed_automod.set_thumbnail(url=automod_thumbnail)
# embed_admin.set_thumbnail(url=admin_thumbnail)