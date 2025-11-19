# src/save_load.py
import json
import os
from datetime import datetime

HISTORY_FILE = "game_history_menu.json"
MAX_HISTORY = 10

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_match(player_name, player_choice, opponent_choice, result):
    history = load_history()
    timestamp = datetime.now().strftime("%H:%M")
    
    if result == "win":
        desc = f"{player_name} Win vs AI"
    elif result == "lose":
        desc = f"AI Win vs {player_name}"
    else:
        desc = "Draw"
    
    new_entry = {"time": timestamp, "desc": desc}
    history.insert(0, new_entry)
    history = history[:MAX_HISTORY]
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except:
        pass  # không crash nếu lỗi