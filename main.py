import sys
import os
import logging
import pygame
import customtkinter as ctk
from src.game import RockPaperScissorsGame
from src.ui import GameUI

# ================================
# Configure Logging
# ================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ================================
# Helper functions
# ================================
def init_pygame_sound():
    """Initialize pygame mixer safely"""
    try:
        pygame.mixer.init()
        logging.info("🎵 Pygame mixer initialized")
    except Exception as e:
        logging.warning("⚠️ Lỗi âm thanh pygame: %s", e)

def ensure_assets():
    """Ensure asset directories exist"""
    for folder in ["assets/images", "assets/sounds"]:
        os.makedirs(folder, exist_ok=True)
        logging.info("✅ Folder checked/created: %s", folder)

def choose_appearance():
    """Choose appearance mode from command line or default"""
    mode = "dark"
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["dark", "light"]:
        mode = sys.argv[1].lower()
    ctk.set_appearance_mode(mode)
    logging.info("🎨 Appearance mode set to: %s", mode)

# ================================
# Main Function
# ================================
def main():
    # Initialize pygame for sound
    init_pygame_sound()

    # CustomTkinter UI Settings
    choose_appearance()
    ctk.set_default_color_theme("blue")

    # Create Game Logic
    try:
        game = RockPaperScissorsGame()
        logging.info("🎮 Game logic initialized")
    except Exception as e:
        logging.error("❌ Lỗi khi tạo game: %s", e)
        sys.exit(1)

    # Start UI
    try:
        app = GameUI(game)
        logging.info("🖥️ UI started")
        app.mainloop()
    except Exception as e:
        logging.error("❌ Lỗi khi chạy UI: %s", e)
        sys.exit(1)


# ================================
# Entry Point
# ================================
if __name__ == "__main__":
    ensure_assets()
    main()
