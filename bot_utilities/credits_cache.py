#!/usr/bin/env python3
"""
Global credits cache manager to prevent API rate limiting.
Updates user credits data every 20 seconds and serves cached data to users.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from threading import Lock
from .credits_ranking import CreditsRanking

class CreditsCache:
    _instance = None
    _lock = Lock()
    _shutdown = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.cached_users: List[Dict[str, Any]] = []
            self.last_update_time: float = 0
            self.update_interval: int = 60  # seconds
            self.is_updating: bool = False
            self.credits_ranking: Optional[CreditsRanking] = None
            self.background_task: Optional[asyncio.Task] = None
            self.initialized = True
    
    def initialize(self, api_key: str, base_url: str = "https://panel.lumixcore.com"):
        """Initialize the credits ranking system."""
        self.credits_ranking = CreditsRanking(base_url=base_url, api_key=api_key)
    
    def get_cached_users(self) -> List[Dict[str, Any]]:
        """
        Get cached users data.
        
        Returns:
            List of cached user dictionaries
        """
        return self.cached_users
    
    def get_last_update_time(self) -> float:
        """Get the timestamp of the last update."""
        return self.last_update_time
    
    def get_time_since_update(self) -> int:
        """Get seconds since last update."""
        return int(time.time() - self.last_update_time)
    
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid (not older than update interval)."""
        return (time.time() - self.last_update_time) < self.update_interval
    
    def needs_update(self) -> bool:
        """Check if cache needs updating."""
        return not self.is_cache_valid() and not self.is_updating
    
    async def update_cache(self):
        """Update the cache with fresh data from the API."""
        if self.is_updating or not self.credits_ranking or self._shutdown:
            return
        
        self.is_updating = True
        try:
            # Run the blocking API calls in a thread executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            users = await loop.run_in_executor(None, self.credits_ranking.get_sorted_users)
            self.cached_users = users
            self.last_update_time = time.time()
        except Exception as e:
            # Silent error handling
            pass
        finally:
            self.is_updating = False
    
    async def start_background_updates(self):
        """Start the background task to update cache every 20 seconds."""
        while not self._shutdown:
            try:
                if self.needs_update():
                    await self.update_cache()
                await asyncio.sleep(5)  # Check every 5 seconds if update is needed
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Silent error handling, wait longer if there's an error
                await asyncio.sleep(10)
    
    def shutdown(self):
        """Gracefully shutdown the cache system."""
        self._shutdown = True
        if self.background_task and not self.background_task.done():
            self.background_task.cancel()
    
    def get_sorted_users(self) -> List[Dict[str, Any]]:
        """
        Get sorted users from cache.
        
        Returns:
            List of user dictionaries sorted by credits
        """
        if not self.cached_users:
            return []
        
        return sorted(self.cached_users, key=lambda x: x['credits'], reverse=True)
    
    def create_leaderboard_view(self, user_id: int, page: int = 0):
        """
        Create a leaderboard view using cached data.
        
        Args:
            user_id: The ID of the user who initiated the command
            page: Starting page number
            
        Returns:
            LeaderboardView instance
        """
        from .credits_ranking import LeaderboardView
        sorted_users = self.get_sorted_users()
        return LeaderboardView(sorted_users, page, user_id)
