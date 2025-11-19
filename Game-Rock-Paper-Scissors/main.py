import sys
import os
import pygame
import customtkinter as ctk
from src.game import RockPaperScissorsGame
from src.ui import GameUI

def main():
    # Initialize pygame for sound
    pygame.mixer.init()
    
    # Set up the application
    ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    # Create the game instance
    game = RockPaperScissorsGame()
    
    # Create and run the UI
    app = GameUI(game)
    app.mainloop()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)
    
    main()
