import random
import json
import os
from enum import Enum
from typing import Optional, Tuple, Dict, List

class Choice(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

class GameResult(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class GameMode(Enum):
    VS_AI = "vs_ai"
    VS_PLAYER = "vs_player"
    AI_VS_AI = "ai_vs_ai"
    VS_LOCAL_PLAYER = "vs_local_player"

class RockPaperScissorsGame:
    def __init__(self):
        self.player1_score = 0
        self.player2_score = 0
        self.round = 1
        self.history: List[Dict] = []
        self.game_mode: Optional[GameMode] = None
        self.player1_name = "Player 1"
        self.player2_name = "AI"
        self.player1_choice: Optional[Choice] = None
        self.player2_choice: Optional[Choice] = None
        self.history_file = "game_history.json"
        self.load_history()

    def set_player_names(self, player1: str, player2: str = "AI"):
        self.player1_name = player1
        self.player2_name = player2

    def set_game_mode(self, mode: GameMode):
        self.game_mode = mode
        if mode == GameMode.AI_VS_AI:
            self.player2_name = "AI 2"

    def get_choices(self) -> List[str]:
        return [choice.value for choice in Choice]

    def make_ai_choice(self) -> Choice:
        # Simple random choice for now
        return random.choice(list(Choice))

    def play_round(self, choice1: Optional[Choice] = None, choice2: Optional[Choice] = None) -> Tuple[GameResult, str]:
        if self.game_mode == GameMode.VS_AI:
            self.player1_choice = choice1
            self.player2_choice = self.make_ai_choice()
        elif self.game_mode == GameMode.AI_VS_AI:
            self.player1_choice = self.make_ai_choice()
            self.player2_choice = self.make_ai_choice()
        else:  # VS_PLAYER
            if choice1 and choice2:
                self.player1_choice = choice1
                self.player2_choice = choice2
            else:
                return GameResult.DRAW, "Waiting for both players"

        result = self.determine_winner()
        self.update_scores(result)
        self.save_round(result)
        self.round += 1
        
        return result, self.get_result_message(result)

    def determine_winner(self) -> GameResult:
        if not self.player1_choice or not self.player2_choice:
            return GameResult.DRAW

        if self.player1_choice == self.player2_choice:
            return GameResult.DRAW
        
        win_conditions = {
            Choice.ROCK: Choice.SCISSORS,
            Choice.PAPER: Choice.ROCK,
            Choice.SCISSORS: Choice.PAPER
        }
        
        return GameResult.WIN if win_conditions[self.player1_choice] == self.player2_choice else GameResult.LOSE

    def update_scores(self, result: GameResult):
        if result == GameResult.WIN:
            self.player1_score += 1
        elif result == GameResult.LOSE:
            self.player2_score += 1

    def get_result_message(self, result: GameResult) -> str:
        if result == GameResult.DRAW:
            return "It's a draw!"
        
        winner = self.player1_name if result == GameResult.WIN else self.player2_name
        return f"{winner} wins! {self.player1_choice.value.capitalize()} beats {self.player2_choice.value}."

    def save_round(self, result: GameResult):
        round_data = {
            "round": self.round,
            "player1": {
                "name": self.player1_name,
                "choice": self.player1_choice.value if self.player1_choice else None,
                "score": self.player1_score
            },
            "player2": {
                "name": self.player2_name,
                "choice": self.player2_choice.value if self.player2_choice else None,
                "score": self.player2_score
            },
            "result": result.value
        }
        self.history.append(round_data)
        self.save_history()

    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []

    def reset_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.round = 1
        self.player1_choice = None
        self.player2_choice = None

    def get_stats(self) -> Dict:
        total_games = len(self.history)
        wins = sum(1 for game in self.history if game["result"] == GameResult.WIN.value)
        losses = sum(1 for game in self.history if game["result"] == GameResult.LOSE.value)
        draws = total_games - wins - losses
        
        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": (wins / total_games * 100) if total_games > 0 else 0
        }
