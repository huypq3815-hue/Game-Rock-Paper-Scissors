from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json
import os

class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"

@dataclass
class PlayerStats:
    total_games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    @property
    def win_rate(self) -> float:
        """Calculate the player's win rate as a percentage"""
        if self.total_games == 0:
            return 0.0
        return (self.wins / self.total_games) * 100
    
    def to_dict(self) -> Dict[str, int]:
        """Convert stats to a dictionary"""
        return {
            "total_games": self.total_games,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'PlayerStats':
        """Create PlayerStats from a dictionary"""
        return cls(
            total_games=data.get("total_games", 0),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),
            draws=data.get("draws", 0)
        )

class Player:
    def __init__(self, name: str, player_type: PlayerType = PlayerType.HUMAN):
        self.name = name
        self.type = player_type
        self.stats = PlayerStats()
        self.current_choice = None
        self.ready = False
        self.stats_file = f"player_{name.lower().replace(' ', '_')}_stats.json"
        
        # Load existing stats if available
        self.load_stats()
    
    def make_choice(self, choice: str):
        """Set the player's current choice"""
        self.current_choice = choice
    
    def reset_choice(self):
        """Reset the player's current choice"""
        self.current_choice = None
    
    def update_stats(self, result: str):
        """Update player statistics based on game result"""
        self.stats.total_games += 1
        
        if result == "win":
            self.stats.wins += 1
        elif result == "lose":
            self.stats.losses += 1
        else:  # draw
            self.stats.draws += 1
        
        # Save stats after each update
        self.save_stats()
    
    def save_stats(self):
        """Save player statistics to a file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving player stats: {e}")
    
    def load_stats(self):
        """Load player statistics from a file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.stats = PlayerStats.from_dict(data)
        except Exception as e:
            print(f"Error loading player stats: {e}")
    
    def get_stats_summary(self) -> str:
        """Get a formatted string of the player's statistics"""
        return (
            f"Games: {self.stats.total_games} | "
            f"Wins: {self.stats.wins} | "
            f"Losses: {self.stats.losses} | "
            f"Draws: {self.stats.draws} | "
            f"Win Rate: {self.stats.win_rate:.1f}%"
        )
    
    def to_dict(self) -> Dict:
        """Convert player data to a dictionary"""
        return {
            "name": self.name,
            "type": self.type.value,
            "ready": self.ready,
            "current_choice": self.current_choice,
            "stats": self.stats.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a Player instance from a dictionary"""
        player = cls(
            name=data["name"],
            player_type=PlayerType(data["type"])
        )
        player.ready = data.get("ready", False)
        player.current_choice = data.get("current_choice")
        player.stats = PlayerStats.from_dict(data.get("stats", {}))
        return player

class PlayerManager:
    def __init__(self):
        self.players: Dict[str, Player] = {}
    
    def add_player(self, name: str, player_type: PlayerType = PlayerType.HUMAN) -> Player:
        """Add a new player"""
        if name in self.players:
            return self.players[name]
            
        player = Player(name, player_type)
        self.players[name] = player
        return player
    
    def get_player(self, name: str) -> Optional[Player]:
        """Get a player by name"""
        return self.players.get(name)
    
    def remove_player(self, name: str):
        """Remove a player"""
        if name in self.players:
            del self.players[name]
    
    def get_all_players(self) -> List[Player]:
        """Get all players"""
        return list(self.players.values())
    
    def reset_choices(self):
        """Reset choices for all players"""
        for player in self.players.values():
            player.reset_choice()
    
    def all_players_ready(self) -> bool:
        """Check if all players are ready"""
        if not self.players:
            return False
        return all(player.ready for player in self.players.values())
    
    def get_leaderboard(self, min_games: int = 0) -> List[Dict]:
        """Get a sorted leaderboard of players"""
        leaderboard = []
        
        for player in self.players.values():
            if player.stats.total_games >= min_games:
                leaderboard.append({
                    "name": player.name,
                    "wins": player.stats.wins,
                    "losses": player.stats.losses,
                    "draws": player.stats.draws,
                    "win_rate": player.stats.win_rate,
                    "total_games": player.stats.total_games
                })
        
        # Sort by win rate (descending), then by number of games (descending)
        leaderboard.sort(key=lambda x: (-x["win_rate"], -x["total_games"]))
        return leaderboard
