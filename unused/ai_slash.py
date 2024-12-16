"""
@bot.tree.command(name="activate", description="Activate AI responses in a channel.")
@commands.guild_only()
@app_commands.describe(channel="Select the channel you want to activate the AI in(optional).")
async def activate_slash(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if await check_blist(interaction, mongodb): return
    await interaction.response.defer(ephemeral=False)
    if channel is None: channel = interaction.channel
    channel_id = channel.id

    if interaction.user.guild_permissions.administrator or interaction.user.id == 1026388699203772477:
        insert_result = await insertdb("ai-channels",channel_id, mongodb)
        if insert_result == "success":
            await interaction.followup.send(embed=Embed(description="Success, now I'll respond to **all messages** in that channel.", color=discord.Colour.green()))
        elif insert_result == "already set":
            await interaction.followup.send(embed=Embed(description=":x: **Error**, that channel is already activated.", colour=discord.Colour.red()))
    else:
        await interaction.followup.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)


@commands.guild_only()
@bot.tree.command(name="deactivate", description="Deactivate AI responses in a channel")
@app_commands.describe(channel="Select the channel you want to activate the AI in(optional).")
async def deactivate_slash(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if await check_blist(interaction, mongodb): return
    await interaction.response.defer(ephemeral=False)
    if channel is None: channel = interaction.channel
    channel_id = channel.id

    if interaction.user.guild_permissions.administrator or interaction.user.id == 1026388699203772477:
        delete_result = await deletedb("ai-channels", channel_id, mongodb)

        if delete_result == "success":
            await interaction.followup.send(embed=Embed(description="**✅ Successfully **disabled** that channel.**", color=discord.Color.green()),)
        elif delete_result == "not found":
            await interaction.followup.send(embed=Embed(description="❌ **Error**, that channel isn't activated.", colour=discord.Colour.red()))
    else:
        await interaction.followup.send(embed=Embed(description="**❌ You don't have permission to use this comamnd.**", color=discord.Color.red()),)


@app_commands.command(name="ask", description="Ask LuminaryAI a question!")
@app_commands.guild_only()
@app_commands.describe(prompt="The question you want to ask LuminaryAI")
async def ask(self, interaction: discord.Interaction, prompt: str):
    if await self.bot.func_checkblist(interaction, self.bot.db): return

    # Use shapes api for now
    await interaction.response.defer(ephemeral=False)
    if prompt is None:
        await interaction.followup.send(embed=discord.Embed(description="**❌ Please include your prompt!**"))
        return

    member_id = str(interaction.user.id)
    history = member_histories_msg.get(member_id, [])

    answer_embed = discord.Embed(
        title="LuminaryAI - Loading",
        description="Please wait while I process your request.",
        color=0x99ccff,
    )
    answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
    answer = await interaction.followup.send(embed=answer_embed)

    generated_message, updated_history = await generate_response_slash(interaction, prompt, history)
    member_histories_msg[member_id] = updated_history

    answer_generated = discord.Embed(
        title="LuminaryAI - Response",
        description=generated_message,
        color=0x99ccff,
    )
    answer_generated.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
    await answer.edit(embed=answer_generated)

@app_commands.command(name="vision", description="Vision an image")
@app_commands.guild_only()
@app_commands.describe(message="Enter your message.")
@app_commands.describe(image_link="Enter the image link.")
async def vision_command(self, interaction: discord.Interaction, message: str, image_link: str):
    if await self.bot.func_checkblist(interaction, self.bot.db): return
    await interaction.response.defer(ephemeral=False)
    response = await vision(message, image_link, self.bot.xet_client)

    response_embed = discord.Embed(
        title="LuminaryAI - vision",
        description=response,
        color=discord.Color.green() if response != "Ouch! Something went wrong!" else discord.Color.red()
    )

    response_embed.set_footer(text="Reply from LuminaryAI Image Vision. LuminaryAI does not guarantee the accuracy of the response provided. The Vision model is currently in **beta**")
    await interaction.followup.send(embed=response_embed)
"""