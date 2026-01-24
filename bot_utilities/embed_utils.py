"""
Utility functions for consistent embed colors across the bot.
"""

import discord

# Define standard colors
DEFAULT_COLOR = 0x708090  # Slate gray
ERROR_COLOR = discord.Color.red()
SUCCESS_COLOR = discord.Color.green()
WARNING_COLOR = discord.Color.orange()
PROCESSING_COLOR = 0x99ccff  # Light blue
LEADERBOARD_COLOR = 0x708090
CONFIRMATION_COLOR = 0xc8dc6c  # Light green

def create_embed(title=None, description=None, color=None, **kwargs):
    """
    Create a Discord embed with standardized color.
    
    Args:
        title: Embed title
        description: Embed description
        color: Embed color (defaults to DEFAULT_COLOR)
        **kwargs: Additional embed parameters
        
    Returns:
        discord.Embed instance
    """
    if color is None:
        color = DEFAULT_COLOR
    
    return discord.Embed(title=title, description=description, color=color, **kwargs)

def create_error_embed(title="Error", description="An error occurred"):
    """Create an error embed with red color."""
    return discord.Embed(title=title, description=description, color=ERROR_COLOR)

def create_success_embed(title="Success", description="Operation completed successfully"):
    """Create a success embed with green color."""
    return discord.Embed(title=title, description=description, color=SUCCESS_COLOR)

def create_warning_embed(title="Warning", description="Warning message"):
    """Create a warning embed with orange color."""
    return discord.Embed(title=title, description=description, color=WARNING_COLOR)

def create_processing_embed(title="Processing", description="Please wait..."):
    """Create a processing embed with light blue color."""
    return discord.Embed(title=title, description=description, color=PROCESSING_COLOR)

def create_leaderboard_embed(title="🏆 Credits Leaderboard", description=None):
    """Create a leaderboard embed with gold color."""
    return discord.Embed(title=title, description=description, color=LEADERBOARD_COLOR)

def create_confirmation_embed(title="Confirmation", description="Please confirm this action"):
    """Create a confirmation embed with light green color."""
    return discord.Embed(title=title, description=description, color=CONFIRMATION_COLOR)
