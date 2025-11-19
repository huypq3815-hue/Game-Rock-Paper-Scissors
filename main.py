import sys
import os
import pygame
import customtkinter as ctk
from src.game import RockPaperScissorsGame
from src.ui import GameUI

def main():
    # Initialize pygame for sound
    try:
        pygame.mixer.init()
    except Exception as e:
        print("⚠️ Lỗi âm thanh pygame:", e)

    # ================================
    # CustomTkinter UI Settings
    # ================================
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue")

    # ================================
    # Create Game Logic
    # ================================
    game = RockPaperScissorsGame()

    # ================================
    # Start UI
    # ================================
    app = GameUI(game)
    app.mainloop()


if __name__ == "__main__":
    # ================================
    # Ensure assets folders exist
    # ================================
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)

    # ================================
    # Run Program
    # ================================
    main()
