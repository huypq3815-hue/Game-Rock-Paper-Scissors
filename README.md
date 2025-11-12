# Rock Paper Scissors Game

A modern and feature-rich Rock Paper Scissors game built with Python, featuring both single-player and multiplayer modes.

## Features

- 🎮 **Multiple Game Modes**:
  - Play against AI with different difficulty levels
  - Local multiplayer (2 players on the same device)
  - Online multiplayer (coming soon)
  - Watch AI vs AI battles

- 🎨 **Beautiful UI**:
  - Modern and responsive interface
  - Animated game elements
  - Sound effects and background music

- 📊 **Statistics & Leaderboards**:
  - Track your win/loss/draw statistics
  - View global leaderboards
  - Game history and match replays

- ⚙️ **Customization**:
  - Choose your player name
  - Select different themes
  - Adjust game settings

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - pip (Python package manager)

2. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/rock-paper-scissors.git
   cd rock-paper-scissors
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. **Single Player Mode**:
   - Run the game: `python main.py`
   - Select "Play vs AI"
   - Choose your move (Rock, Paper, or Scissors)
   - The AI will make its move automatically
   - First to 3 points wins!

2. **Local Multiplayer**:
   - Run the game
   - Select "Local Multiplayer"
   - Take turns with a friend on the same device

3. **Online Multiplayer** (coming soon):
   - One player creates a room
   - Other players join using the room code
   - Play against friends over the internet

## Controls

- **Mouse**: Click buttons to make your selection
- **Keyboard Shortcuts**:
  - `R`: Rock
  - `P`: Paper
  - `S`: Scissors
  - `ESC`: Return to main menu
  - `F11`: Toggle fullscreen

## Project Structure

```
rock-paper-scissors/
├── assets/               # Game assets (images, sounds, etc.)
├── src/                  # Source code
│   ├── __init__.py
│   ├── game.py           # Main game logic
│   ├── player.py         # Player class and statistics
│   ├── network.py        # Network functionality for multiplayer
│   └── ui/               # User interface components
│       ├── __init__.py
│       ├── main_menu.py  # Main menu screen
│       ├── game_ui.py    # Game screen
│       └── widgets/      # Custom UI widgets
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- Python 3.8+
- Pygame
- CustomTkinter
- Pillow (PIL Fork)

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ using Python
- Special thanks to all contributors
- Inspired by classic Rock Paper Scissors

---

🎮 **Happy Playing!** 🎮
