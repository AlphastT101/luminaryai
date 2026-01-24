#!/usr/bin/env python3
"""
Discord bot utility to fetch and display user credits from Jexactyl panel API.
Sorts users from highest to lowest credits with pagination support.
"""

import requests
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
import discord
from discord.ui import View, Button
from discord import Interaction
from .embed_utils import create_leaderboard_embed

class LeaderboardView(View):
    def __init__(self, users: List[Dict[str, Any]], page: int = 0, original_user_id: int = None):
        super().__init__(timeout=60.0)
        self.users = users
        self.page = page
        self.per_page = 20
        self.total_pages = (len(users) - 1) // self.per_page + 1
        self.message = None
        self.original_user_id = original_user_id
        
        # Add buttons
        self.add_item(Button(label="◀", style=discord.ButtonStyle.primary, custom_id="prev"))
        self.add_item(Button(label="▶", style=discord.ButtonStyle.primary, custom_id="next"))
        self.add_item(Button(label="❌", style=discord.ButtonStyle.danger, custom_id="close"))
        
        # Set button callbacks
        for item in self.children:
            if item.custom_id == "prev":
                item.callback = self.prev_callback
            elif item.custom_id == "next":
                item.callback = self.next_callback
            elif item.custom_id == "close":
                item.callback = self.close_callback
    
    async def prev_callback(self, interaction: Interaction):
        if interaction.user.id != self.original_user_id:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Don't disturb other users :)", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
    
    async def next_callback(self, interaction: Interaction):
        if interaction.user.id != self.original_user_id:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Don't disturb other users :)", ephemeral=True)
            return
        
        if self.page < self.total_pages - 1:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()
    
    async def close_callback(self, interaction: Interaction):
        if interaction.user.id != self.original_user_id:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Don't disturb other users :)", ephemeral=True)
            return
        
        await interaction.response.edit_message(view=None)
        self.stop()
    
    async def update_message(self, interaction: Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_embed(self) -> discord.Embed:
        start_idx = self.page * self.per_page
        end_idx = start_idx + self.per_page
        page_users = self.users[start_idx:end_idx]
        
        embed = create_leaderboard_embed(
            title="Panel Credits Leaderboard"
        )
        
        # Create leaderboard content
        leaderboard_text = ""
        for i, user in enumerate(page_users, start=start_idx + 1):
            leaderboard_text += f"**{i}.** {user['username']} - `{user['credits']}` credits\n"
        
        embed.description = leaderboard_text
        
        # Footer with total users and page info
        embed.set_footer(text=f"{len(self.users)} total users, page {self.page + 1}/{self.total_pages}")
        
        return embed
    
    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)

class CreditsRanking:
    def __init__(self, base_url: str = "https://panel.lumixcore.com", api_key: str = None):
        """
        Initialize the CreditsRanking class.
        
        Args:
            base_url: Base URL of the Jexactyl panel
            api_key: API key for authentication (Application API)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
    
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Fetch all users from the API.
        
        Returns:
            List of user dictionaries
        """
        url = f"{self.base_url}/api/application/users"
        
        try:
            response = self.session.get(url, params={'per_page': 1000})
            
            # Handle rate limiting
            if response.status_code == 429:
                return []
            
            response.raise_for_status()
            
            data = response.json()
            
            # Handle JSON API response format
            if 'data' in data:
                users = []
                for item in data['data']:
                    if 'attributes' in item:
                        users.append(item['attributes'])
                    else:
                        users.append(item)
                return users
            else:
                return data if isinstance(data, list) else []
                
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                return []
            else:
                return []
    
    def get_user_resources(self, user_id: int) -> Dict[str, Any]:
        """
        Get user resources including store_balance (credits).
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary with user resources
        """
        url = f"{self.base_url}/api/application/users/{user_id}/resources"
        
        try:
            response = self.session.get(url)
            
            # Handle rate limiting
            if response.status_code == 429:
                return {'balance': 0, 'cpu': 0, 'memory': 0, 'disk': 0, 'slots': 0, 'ports': 0, 'backups': 0, 'databases': 0}
            
            response.raise_for_status()
            
            data = response.json()
            
            # Handle JSON API response format
            if 'attributes' in data:
                return data['attributes']
            elif 'data' in data:
                if 'attributes' in data['data']:
                    return data['data']['attributes']
                else:
                    return data['data']
            else:
                return data
                
        except requests.exceptions.RequestException as e:
            if "429" in str(e):
                return {'balance': 0, 'cpu': 0, 'memory': 0, 'disk': 0, 'slots': 0, 'ports': 0, 'backups': 0, 'databases': 0}
            else:
                return {}
    
    def fetch_all_users_with_credits(self) -> List[Dict[str, Any]]:
        """
        Fetch all users with their credits.
        
        Returns:
            List of user dictionaries with credits information
        """
        users = self.get_users()
        users_with_credits = []
        
        for i, user in enumerate(users, 1):
            user_id = user.get('id')
            if not user_id:
                continue
                
            # Add delay to prevent rate limiting
            if i > 1 and i % 50 == 0:
                time.sleep(5)
            elif i > 1:
                time.sleep(0.1)  # Small delay between each request
                
            # Get user resources for credits
            resources = self.get_user_resources(user_id)
            
            # Extract user info
            user_data = {
                'id': user_id,
                'username': user.get('username', 'Unknown'),
                'email': user.get('email', ''),
                'credits': resources.get('balance', 0),  # Changed from store_balance to balance
                'cpu': resources.get('cpu', 0),
                'memory': resources.get('memory', 0),
                'disk': resources.get('disk', 0),
                'slots': resources.get('slots', 0),
                'ports': resources.get('ports', 0),
                'backups': resources.get('backups', 0),
                'databases': resources.get('databases', 0),
            }
            
            users_with_credits.append(user_data)
        
        return users_with_credits
    
    def get_sorted_users(self) -> List[Dict[str, Any]]:
        """
        Get users sorted by credits from highest to lowest.
        
        Returns:
            List of user dictionaries sorted by credits
        """
        users = self.fetch_all_users_with_credits()
        return sorted(users, key=lambda x: x['credits'], reverse=True)
    
    def create_leaderboard_view(self, user_id: int, page: int = 0) -> LeaderboardView:
        """
        Create a leaderboard view with pagination.
        
        Args:
            user_id: The ID of the user who initiated the command
            page: Starting page number
            
        Returns:
            LeaderboardView instance
        """
        sorted_users = self.get_sorted_users()
        return LeaderboardView(sorted_users, page, user_id)
