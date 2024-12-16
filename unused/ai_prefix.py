"""
@bot.command(name='activate')
@commands.cooldown(1, 10, commands.BucketType.user)
async def start(ctx):
    channel_id = ctx.channel.id

    if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
        insert_result = await insertdb("ai-channels",channel_id, mongodb)
        if insert_result == "success":
            await ctx.send(embed=Embed(description="Success, now I'll respond to **all messages** in this channel.", color=discord.Colour.green()))
        elif insert_result == "already set":
            await ctx.send(embed=Embed(description=":x: **Error**, this channel is already activated.", colour=discord.Colour.red()))
    else:
        await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)

@bot.command(name='deactivate')
@commands.cooldown(1, 10, commands.BucketType.user)
async def stop(ctx):

    channel_id = ctx.channel.id

    if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
        delete_result = await deletedb("ai-channels", channel_id, mongodb)

        if delete_result == "success":
            await ctx.send(embed=Embed(description="**Successfully disabled this channel.**", color=discord.Color.green()),)
        elif delete_result == "not found":
            await ctx.send(embed=Embed(description=":x: **Error**, this channel isn't activated.", colour=discord.Colour.red()))
    else:
        await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)


@commands.command(name='ask')
@commands.cooldown(1, 80, commands.BucketType.user)
async def answer_command(self, ctx, *, args: str = None):
    if args is None:
        await embed(ctx, "LuminaryAI - Error", "Please enter your question.", color=0x99ccff)
        return
    # Get or create member-specific history
    member_id = str(ctx.author.id)  # Using member ID as the key
    history = member_histories_msg.get(member_id, [])

    answer_embed = discord.Embed(
        title="LuminaryAI - Loading",
        description="Please wait while I process your request.",
        color=0x99ccff,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
    answer = await ctx.reply(embed=answer_embed)

    user_input = args
    generated_message, updated_history = await generate_response_cmd(ctx, user_input, history)
    member_histories_msg[member_id] = updated_history


    answer_generated = discord.Embed(
        title="LuminaryAI - Response",
        description=generated_message,
        color=0x99ccff,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    answer_generated.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
    await answer.edit(embed=answer_generated)

"""