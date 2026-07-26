import discord

from bot import config


def create_embed(title=None, description=None, color=None, **kwargs):
    if color is None:
        color = config.EMBED_COLOR_DEFAULT
    return discord.Embed(title=title, description=description, color=color, **kwargs)


def create_error_embed(title="Error", description="An error occurred"):
    return discord.Embed(title=title, description=description, color=config.EMBED_COLOR_ERROR)


def create_success_embed(title="Success", description="Operation completed successfully"):
    return discord.Embed(title=title, description=description, color=config.EMBED_COLOR_SUCCESS)


def create_warning_embed(title="Warning", description="Warning message"):
    return discord.Embed(title=title, description=description, color=config.EMBED_COLOR_WARNING)


def create_processing_embed(title="Processing", description="Please wait..."):
    return discord.Embed(title=title, description=description, color=config.EMBED_COLOR_PROCESSING)


def create_confirmation_embed(title="Confirmation", description="Please confirm this action"):
    return discord.Embed(title=title, description=description, color=config.EMBED_COLOR_CONFIRMATION)
