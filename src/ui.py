import os
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional, Callable, Dict, Any
import pygame
import json
from enum import Enum
from .game import RockPaperScissorsGame, GameMode, Choice, GameResult
from .network import NetworkManager, NetworkMessageType

class GameUI(ctk.CTk):
    def __init__(self, game: RockPaperScissorsGame):
        super().__init__()
        
        self.game = game
        self.images: Dict[str, ctk.CTkImage] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_frame = None
        self.network_manager: Optional[NetworkManager] = None
        self.opponent_choice: Optional[Choice] = None
        self.opponent_ready = False
        
        # Retro color scheme
        self.retro_colors = {
            "bg": "#0a0a0a",  # Very dark background
            "fg": "#00ff41",  # Neon green (Matrix style)
            "accent": "#ffaa00",  # Neon orange
            "accent2": "#00ffff",  # Cyan
            "accent3": "#ff00ff",  # Magenta
            "text": "#00ff41",  # Neon green text
            "text_secondary": "#ffff00",  # Yellow
            "button": "#00ff41",  # Neon green buttons
            "button_hover": "#00cc33",  # Darker green
            "button_danger": "#ff3333",  # Red
            "button_danger_hover": "#cc0000",
            "frame": "#1a1a1a",  # Dark frame
            "border": "#00ff41",  # Neon border
            "error": "#ff3333"  # Error red
        }
        
        # Retro font
        self.retro_font = ("Courier New", 14, "bold")
        self.retro_font_large = ("Courier New", 24, "bold")
        self.retro_font_xlarge = ("Courier New", 32, "bold")
        
        # Configure window with retro theme
        self.title("Rock Paper Scissors - RETRO")
        self.geometry("800x600")
        self.minsize(800, 600)
        self.configure(bg=self.retro_colors["bg"])
        
        # Initialize sounds
        self.load_sounds()
        
        # Load images
        self.load_images()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Show main menu
        self.show_main_menu()
    
    def load_images(self):
        """Load all required images"""
        try:
            # Load choice images
            for choice in ["rock", "paper", "scissors"]:
                img_path = os.path.join("assets", "images", f"{choice}.png")
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((120, 120), Image.LANCZOS)
                    self.images[choice] = ctk.CTkImage(light_image=img, size=(120, 120))
            
            # Load logo
            logo_path = os.path.join("assets", "images", "logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((300, 100), Image.LANCZOS)
                self.images["logo"] = ctk.CTkImage(light_image=logo_img, size=(300, 100))
                
        except Exception as e:
            print(f"Error loading images: {e}")
    
    def create_synthetic_sound(self, sound_type: str):
        """Create a synthetic sound effect if file doesn't exist"""
        try:
            import numpy as np
            import wave
            import io
            
            sample_rate = 22050
            duration = 0.1 if sound_type == "click" else 0.5
            
            if sound_type == "click":
                # Short beep for click
                frequency = 800
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave_data = np.sin(2 * np.pi * frequency * t) * 0.3
                # Add fade out
                fade_samples = int(sample_rate * 0.05)
                wave_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            elif sound_type == "win":
                # Rising tone for win
                t = np.linspace(0, duration, int(sample_rate * duration))
                frequency = np.linspace(400, 800, len(t))
                wave_data = np.sin(2 * np.pi * frequency * t) * 0.3
            elif sound_type == "lose":
                # Falling tone for lose
                t = np.linspace(0, duration, int(sample_rate * duration))
                frequency = np.linspace(600, 200, len(t))
                wave_data = np.sin(2 * np.pi * frequency * t) * 0.3
            elif sound_type == "draw":
                # Neutral tone for draw
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave_data = np.sin(2 * np.pi * 400 * t) * 0.2
            else:
                return None
            
            # Convert to 16-bit integer
            wave_data = (wave_data * 32767).astype(np.int16)
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(wave_data.tobytes())
            
            wav_buffer.seek(0)
            return pygame.mixer.Sound(wav_buffer)
        except Exception as e:
            print(f"Error creating synthetic sound {sound_type}: {e}")
            return None
    
    def load_sounds(self):
        """Load all required sound effects"""
        try:
            sound_files = {
                "win": "win.mp3",
                "lose": "lose.mp3",
                "draw": "draw.mp3",
                "click": "click.mp3"
            }
            
            for sound_name, filename in sound_files.items():
                sound_path = os.path.join("assets", "sounds", filename)
                if os.path.exists(sound_path):
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                        # Try to create synthetic sound
                        synthetic = self.create_synthetic_sound(sound_name)
                        if synthetic:
                            self.sounds[sound_name] = synthetic
                else:
                    # Create synthetic sound if file doesn't exist
                    synthetic = self.create_synthetic_sound(sound_name)
                    if synthetic:
                        self.sounds[sound_name] = synthetic
                        print(f"Created synthetic sound for {sound_name}")
        except Exception as e:
            print(f"Error loading sounds: {e}")
    
    def play_sound(self, sound_name: str):
        """Play a sound effect if available"""
        if sound_name in self.sounds:
            try:
                pygame.mixer.Sound.play(self.sounds[sound_name])
            except:
                pass
    
    def create_retro_label(self, parent, text, font=None, text_color=None, **kwargs):
        """Create a retro-styled label"""
        if font is None:
            font = self.retro_font
        if text_color is None:
            text_color = self.retro_colors["text"]
        return ctk.CTkLabel(
            parent,
            text=text,
            font=font,
            text_color=text_color,
            **kwargs
        )
    
    def create_retro_button(self, parent, text, command, fg_color=None, hover_color=None, 
                           text_color="#000000", border_color=None, **kwargs):
        """Create a retro-styled button"""
        if fg_color is None:
            fg_color = self.retro_colors["button"]
        if hover_color is None:
            hover_color = self.retro_colors["button_hover"]
        if border_color is None:
            border_color = self.retro_colors["border"]
        return ctk.CTkButton(
            parent,
            text=text,
            font=self.retro_font,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            border_color=border_color,
            border_width=2,
            command=command,
            **kwargs
        )
    
    def clear_frame(self):
        """Clear the current frame"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ctk.CTkFrame(
            self,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(0, weight=1)
    
    def show_main_menu(self):
        """Show the main menu"""
        self.clear_frame()
        
        # Add logo if available
        if "logo" in self.images:
            logo_label = ctk.CTkLabel(self.current_frame, image=self.images["logo"], text="")
            logo_label.pack(pady=(0, 40))
        else:
            title = ctk.CTkLabel(
                self.current_frame,
                text=">>> ROCK PAPER SCISSORS <<<",
                font=self.retro_font_xlarge,
                text_color=self.retro_colors["text"]
            )
            title.pack(pady=(0, 40))
        
        # Player name entry
        name_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        name_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(
            name_frame,
            text="> YOUR NAME:",
            font=self.retro_font,
            text_color=self.retro_colors["text"]
        ).pack(side="left", padx=(0, 10))
        self.player_name = ctk.CTkEntry(
            name_frame,
            width=200,
            placeholder_text="PLAYER",
            font=self.retro_font,
            fg_color=self.retro_colors["bg"],
            border_color=self.retro_colors["border"],
            text_color=self.retro_colors["text"]
        )
        self.player_name.pack(side="left")
        
        # Game mode buttons
        button_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        button_frame.pack(expand=True, fill="both", pady=20)
        
        vs_ai_btn = ctk.CTkButton(
            button_frame,
            text="> PLAY VS AI",
            font=self.retro_font_large,
            height=50,
            fg_color=self.retro_colors["button"],
            hover_color=self.retro_colors["button_hover"],
            text_color="#000000",
            border_color=self.retro_colors["border"],
            border_width=2,
            command=lambda: self.start_game(GameMode.VS_AI)
        )
        vs_ai_btn.pack(fill="x", pady=10, padx=100)
        
        vs_local_btn = ctk.CTkButton(
            button_frame,
            text="> PLAY LOCAL (2 PLAYERS)",
            font=self.retro_font_large, 
            height=50,
            fg_color=self.retro_colors["button"],
            hover_color=self.retro_colors["button_hover"],
            text_color="#000000",
            border_color=self.retro_colors["border"],
            border_width=2,
            command=lambda: [self.play_sound("click"), self.show_local_2player_menu()]
        )
        vs_local_btn.pack(fill="x", pady=10, padx=100)
        
        vs_player_btn = ctk.CTkButton(
            button_frame,
            text="> PLAY ONLINE",
            font=self.retro_font_large,
            height=50,
            fg_color=self.retro_colors["accent"],
            hover_color="#ff8800",
            text_color="#000000",
            border_color=self.retro_colors["accent"],
            border_width=2,
            command=lambda: [self.play_sound("click"), self.show_online_menu()]
        )
        vs_player_btn.pack(fill="x", pady=10, padx=100)
        
        ai_vs_ai_btn = ctk.CTkButton(
            button_frame,
            text="> WATCH AI VS AI",
            font=self.retro_font_large,
            height=50,
            fg_color=self.retro_colors["accent2"],
            hover_color="#00cccc",
            text_color="#000000",
            border_color=self.retro_colors["accent2"],
            border_width=2,
            command=lambda: self.start_game(GameMode.AI_VS_AI)
        )
        ai_vs_ai_btn.pack(fill="x", pady=10, padx=100)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text="> EXIT",
            font=self.retro_font,
            fg_color=self.retro_colors["button_danger"],
            hover_color=self.retro_colors["button_danger_hover"],
            height=40,
            text_color="#FFFFFF",
            border_color=self.retro_colors["button_danger"],
            border_width=2,
            command=lambda: [self.play_sound("click"), self.quit()]
        )
        exit_btn.pack(fill="x", pady=(20, 0), padx=100)
    
    def show_local_2player_menu(self):
        """Show the local 2-player setup menu"""
        self.clear_frame()
        
        title = self.create_retro_label(
            self.current_frame,
            text=">>> LOCAL 2-PLAYER GAME <<<",
            font=self.retro_font_xlarge
        )
        title.pack(pady=(0, 30))
        
        # Player 1 name
        player1_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        player1_frame.pack(fill="x", pady=10, padx=100)
        
        self.create_retro_label(player1_frame, text="> PLAYER 1 NAME:",).pack(side="left", padx=(0, 10))
        self.player1_local_name = ctk.CTkEntry(
            player1_frame,
            width=200,
            placeholder_text="PLAYER 1",
            font=self.retro_font,
            fg_color=self.retro_colors["bg"],
            border_color=self.retro_colors["border"],
            text_color=self.retro_colors["text"]
        )
        self.player1_local_name.pack(side="left")
        
        # Player 2 name
        player2_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        player2_frame.pack(fill="x", pady=10, padx=100)
        
        self.create_retro_label(player2_frame, text="> PLAYER 2 NAME:",).pack(side="left", padx=(0, 10))
        self.player2_local_name = ctk.CTkEntry(
            player2_frame,
            width=200,
            placeholder_text="PLAYER 2",
            font=self.retro_font,
            fg_color=self.retro_colors["bg"],
            border_color=self.retro_colors["border"],
            text_color=self.retro_colors["text"]
        )
        self.player2_local_name.pack(side="left")
        
        # Start button
        start_btn = self.create_retro_button(
            self.current_frame,
            text="> START GAME",
            command=self.start_local_2player_game,
            font=self.retro_font_large,
            height=50
        )
        start_btn.pack(fill="x", pady=20, padx=100)
        
        # Back button
        back_btn = self.create_retro_button(
            self.current_frame,
            text="> BACK TO MAIN MENU",
            command=lambda: [self.play_sound("click"), self.show_main_menu()],
            height=40
        )
        back_btn.pack(pady=(10, 0))
    
    def start_local_2player_game(self):
        """Start a local 2-player game"""
        self.game.set_game_mode(GameMode.VS_LOCAL_PLAYER)
        player1_name = self.player1_local_name.get() or "Player 1"
        player2_name = self.player2_local_name.get() or "Player 2"
        self.game.set_player_names(player1_name, player2_name)
        self.show_local_2player_game_screen()

    def show_online_menu(self):
        """Show the online game menu"""
        self.clear_frame()
        
        title = self.create_retro_label(
            self.current_frame,
            text=">>> ONLINE GAME <<<",
            font=self.retro_font_xlarge
        )
        title.pack(pady=(0, 30))
        
        # Create room button
        create_btn = self.create_retro_button(
            self.current_frame,
            text="> CREATE ROOM",
            command=self.create_room,
            font=self.retro_font_large,
            height=50,
            fg_color=self.retro_colors["accent"]
        )
        create_btn.pack(fill="x", pady=10, padx=100)
        
        # Join room section
        join_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        join_frame.pack(fill="x", pady=20, padx=100)
        
        self.room_code = ctk.CTkEntry(
            join_frame,
            placeholder_text="ENTER ROOM CODE",
            font=self.retro_font,
            fg_color=self.retro_colors["bg"],
            border_color=self.retro_colors["border"],
            text_color=self.retro_colors["text"]
        )
        self.room_code.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        join_btn = self.create_retro_button(
            join_frame,
            text="> JOIN",
            command=self.join_room,
            width=80
        )
        join_btn.pack(side="right")
        
        # Back button
        back_btn = self.create_retro_button(
            self.current_frame,
            text="> BACK TO MAIN MENU",
            command=lambda: [self.play_sound("click"), self.show_main_menu()],
            height=40
        )
        back_btn.pack(pady=(30, 0))
    
    def create_room(self):
        """Create a new online game room"""
        # Initialize network manager
        self.network_manager = NetworkManager()
        
        # Set up message handlers
        self.network_manager.set_message_handler(
            NetworkMessageType.PLAYER_CHOICE,
            self._handle_opponent_choice
        )
        
        # Start server
        room_code = self.network_manager.create_room()
        if room_code:
            self.game.set_game_mode(GameMode.VS_PLAYER)
            self.game.set_player_names(
                self.player_name.get() or "Player 1",
                "Opponent"
            )
            self.show_waiting_for_opponent(room_code)
        else:
            self._show_error("Failed to create room")
    
    def join_room(self):
        """Join an existing game room"""
        room_code = self.room_code.get().strip()
        if not room_code:
            self._show_error("Please enter a room code")
            return
            
        self.play_sound("click")
        
        # Initialize network manager
        self.network_manager = NetworkManager()
        
        # Set up message handlers
        self.network_manager.set_message_handler(
            NetworkMessageType.PLAYER_CHOICE,
            self._handle_opponent_choice
        )
        
        # Try to join
        if self.network_manager.join_room(room_code):
            self.game.set_game_mode(GameMode.VS_PLAYER)
            self.game.set_player_names(
                self.player_name.get() or "Player 2",
                "Opponent"
            )
            self.show_online_game_screen()
        else:
            self._show_error("Failed to connect to room. Check the room code and try again.")
    
    def _handle_opponent_choice(self, message: Dict[str, Any]):
        """Handle opponent's choice received over network"""
        try:
            choice_str = message.get("data", {}).get("choice")
            if choice_str:
                self.opponent_choice = Choice(choice_str)
                self.opponent_ready = True
        except Exception as e:
            print(f"Error handling opponent choice: {e}")
    
    def _show_error(self, error_message: str):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("ERROR")
        dialog.geometry("400x150")
        dialog.configure(bg=self.retro_colors["bg"])
        dialog.grab_set()
        
        label = self.create_retro_label(
            dialog,
            text=f">>> ERROR <<<\n{error_message}",
            text_color=self.retro_colors["error"]
        )
        label.pack(pady=20, padx=20)
        
        btn = self.create_retro_button(
            dialog,
            text="> OK",
            command=lambda: [self.play_sound("click"), dialog.destroy()],
            fg_color=self.retro_colors["button_danger"],
            text_color="#FFFFFF"
        )
        btn.pack(pady=10)
    
    def show_local_2player_game_screen(self):
        """Show the local 2-player game screen with alternating player inputs"""
        self.clear_frame()
        
        # Configure grid
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(1, weight=1)
        
        # Header with scores
        header = ctk.CTkFrame(
            self.current_frame,
            height=60,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        self.create_retro_label(
            player1_frame,
            text=f"> {self.game.player1_name.upper()}",
            font=self.retro_font
        ).pack()
        
        self.player1_score_label = self.create_retro_label(
            player1_frame,
            text=f"SCORE: {self.game.player1_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = self.create_retro_label(
            round_frame,
            text=f">>> ROUND {self.game.round} <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["accent"]
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        self.create_retro_label(
            player2_frame,
            text=f"{self.game.player2_name.upper()} <",
            font=self.retro_font
        ).pack()
        
        self.player2_score_label = self.create_retro_label(
            player2_frame,
            text=f"SCORE: {self.game.player2_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(
            self.current_frame,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        game_area.grid(row=1, column=0, sticky="nsew")
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        # Initialize local 2-player state
        self.local_player1_choice = None
        self.local_player2_choice = None
        
        # Show Player 1's input screen
        self.show_local_player_input(1, game_area)
    
    def show_local_player_input(self, player_num: int, game_area):
        """Show input screen for a local player"""
        # Clear the game area
        for widget in game_area.winfo_children():
            widget.destroy()
        
        player_name = self.game.player1_name if player_num == 1 else self.game.player2_name
        
        # Title
        title = self.create_retro_label(
            game_area,
            text=f">>> {player_name.upper()}'S TURN <<<",
            font=self.retro_font_xlarge,
            text_color=self.retro_colors["accent"]
        )
        title.grid(row=0, column=0, columnspan=3, pady=(20, 10))
        
        # Instruction
        instruction = self.create_retro_label(
            game_area,
            text="> CHOOSE YOUR MOVE:",
            font=self.retro_font_large
        )
        instruction.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        choice_colors = [self.retro_colors["button"], self.retro_colors["accent"], self.retro_colors["accent2"]]
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = self.create_retro_button(
                buttons_frame,
                text=f"> {choice.upper()}",
                command=lambda c=choice, p=player_num: self.local_player_choice(c, p),
                width=120,
                height=40,
                fg_color=choice_colors[i]
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Warning message (don't let other player see)
        warning = self.create_retro_label(
            game_area,
            text=">>> WARNING: OTHER PLAYER SHOULD NOT LOOK! <<<",
            font=self.retro_font,
            text_color=self.retro_colors["error"]
        )
        warning.grid(row=3, column=0, columnspan=3, pady=(20, 0))
    
    def local_player_choice(self, choice: str, player_num: int):
        """Handle choice from a local player"""
        self.play_sound("click")
        
        if player_num == 1:
            self.local_player1_choice = Choice(choice)
            # Show waiting message and then Player 2's input
            self.show_local_player_waiting()
        else:
            self.local_player2_choice = Choice(choice)
            # Both players have chosen, play the round
            self.play_local_2player_round()
    
    def show_local_player_waiting(self):
        """Show waiting screen between players"""
        self.clear_frame()
        
        waiting = self.create_retro_label(
            self.current_frame,
            text=">>> PLAYER 1'S CHOICE SAVED! <<<",
            font=self.retro_font_xlarge,
            text_color=self.retro_colors["accent"]
        )
        waiting.pack(pady=(50, 20))
        
        instruction = self.create_retro_label(
            self.current_frame,
            text="> GIVE COMPUTER TO PLAYER 2 AND CLICK READY",
            font=self.retro_font_large
        )
        instruction.pack(pady=20)
        
        # Get the game area frame to pass to show_local_player_input
        game_area = ctk.CTkFrame(
            self.current_frame,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        game_area.pack(expand=True, fill="both", padx=20, pady=20)
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        ready_btn = self.create_retro_button(
            self.current_frame,
            text="> READY - SHOW PLAYER 2 INPUT",
            command=lambda: [self.play_sound("click"), self.show_local_player_input(2, game_area)],
            font=self.retro_font_large,
            height=50
        )
        ready_btn.pack(pady=20, padx=100, fill="x")
    
    def play_local_2player_round(self):
        """Play a round with two local players"""
        result, message = self.game.play_round(self.local_player1_choice, self.local_player2_choice)
        self.show_local_2player_result(result, message)
    
    def show_local_2player_result(self, result: GameResult, message: str):
        """Show the result of a local 2-player round"""
        self.clear_frame()
        
        # Update scores
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(1, weight=1)
        
        # Header with scores
        header = ctk.CTkFrame(
            self.current_frame,
            height=60,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        self.create_retro_label(
            player1_frame,
            text=f"> {self.game.player1_name.upper()}",
            font=self.retro_font
        ).pack()
        
        self.create_retro_label(
            player1_frame,
            text=f"SCORE: {self.game.player1_score}",
            text_color=self.retro_colors["text_secondary"]
        ).pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.create_retro_label(
            round_frame,
            text=f">>> ROUND {self.game.round - 1} <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["accent"]
        ).pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        self.create_retro_label(
            player2_frame,
            text=f"{self.game.player2_name.upper()} <",
            font=self.retro_font
        ).pack()
        
        self.create_retro_label(
            player2_frame,
            text=f"SCORE: {self.game.player2_score}",
            text_color=self.retro_colors["text_secondary"]
        ).pack()
        
        # Result area
        result_area = ctk.CTkFrame(
            self.current_frame,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        result_area.grid(row=1, column=0, sticky="nsew")
        result_area.grid_columnconfigure((0, 1, 2), weight=1)
        result_area.grid_rowconfigure(1, weight=1)
        
        # Show choices
        choices_frame = ctk.CTkFrame(result_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=20)
        
        self.create_retro_label(
            choices_frame,
            text=f"{self.game.player1_name.upper()}: {self.game.player1_choice.value.upper()}",
            font=self.retro_font
        ).pack(side="left", padx=40)
        
        self.create_retro_label(
            choices_frame,
            text="VS",
            font=self.retro_font,
            text_color=self.retro_colors["accent"]
        ).pack(side="left", padx=20)
        
        self.create_retro_label(
            choices_frame,
            text=f"{self.game.player2_choice.value.upper()}: {self.game.player2_name.upper()}",
            font=self.retro_font
        ).pack(side="left", padx=40)
        
        # Result message
        result_label = self.create_retro_label(
            result_area,
            text=f">>> {message.upper()} <<<",
            font=self.retro_font_xlarge,
            text_color=self.retro_colors["accent"]
        )
        result_label.grid(row=1, column=0, columnspan=3, pady=40)
        
        # Play sound
        if result == GameResult.WIN:
            self.play_sound("win")
        elif result == GameResult.LOSE:
            self.play_sound("lose")
        else:
            self.play_sound("draw")
        
        # Action buttons
        button_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(20, 0))
        
        next_btn = self.create_retro_button(
            button_frame,
            text="> NEXT ROUND",
            command=lambda: [self.play_sound("click"), self.show_local_2player_game_screen()],
            width=120,
            height=40
        )
        next_btn.pack(side="left", padx=10)
        
        menu_btn = self.create_retro_button(
            button_frame,
            text="> MAIN MENU",
            command=lambda: [self.play_sound("click"), self.show_main_menu()],
            width=120,
            height=40
        )
        menu_btn.pack(side="left", padx=10)
    
    def show_waiting_for_opponent(self, room_code: str):
        """Show waiting screen for opponent to join"""
        self.clear_frame()
        
        title = self.create_retro_label(
            self.current_frame,
            text=">>> WAITING FOR OPPONENT <<<",
            font=self.retro_font_xlarge,
            text_color=self.retro_colors["accent"]
        )
        title.pack(pady=(50, 30))
        
        info_label = self.create_retro_label(
            self.current_frame,
            text="> SHARE THIS ROOM CODE WITH YOUR OPPONENT:",
            font=self.retro_font
        )
        info_label.pack(pady=(0, 10))
        
        # Room code display with copy button
        code_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        code_frame.pack(pady=20)
        
        code_label = self.create_retro_label(
            code_frame,
            text=f">>> {room_code} <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["accent"]
        )
        code_label.pack(side="left", padx=(0, 10))
        
        copy_btn = self.create_retro_button(
            code_frame,
            text="> COPY",
            command=lambda: self.copy_to_clipboard(room_code),
            width=80
        )
        copy_btn.pack(side="left")
        
        # Waiting indicator
        waiting_label = self.create_retro_label(
            self.current_frame,
            text=">>> WAITING... <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["text_secondary"]
        )
        waiting_label.pack(pady=(30, 0))
        
        # Cancel button
        cancel_btn = self.create_retro_button(
            self.current_frame,
            text="> CANCEL",
            command=self.cancel_online_game,
            height=40,
            fg_color=self.retro_colors["button_danger"],
            text_color="#FFFFFF"
        )
        cancel_btn.pack(pady=(30, 0), padx=100, fill="x")
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.play_sound("click")
    
    def show_online_game_screen(self):
        """Show the online game screen"""
        self.clear_frame()
        
        # Configure grid
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(1, weight=1)
        
        # Header with scores
        header = ctk.CTkFrame(
            self.current_frame,
            height=60,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        self.create_retro_label(
            player1_frame,
            text=f"> {self.game.player1_name.upper()}",
            font=self.retro_font
        ).pack()
        
        self.player1_score_label = self.create_retro_label(
            player1_frame,
            text=f"SCORE: {self.game.player1_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = self.create_retro_label(
            round_frame,
            text=f">>> ROUND {self.game.round} <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["accent"]
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        self.create_retro_label(
            player2_frame,
            text=f"{self.game.player2_name.upper()} <",
            font=self.retro_font
        ).pack()
        
        self.player2_score_label = self.create_retro_label(
            player2_frame,
            text=f"SCORE: {self.game.player2_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(
            self.current_frame,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        game_area.grid(row=1, column=0, sticky="nsew")
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        # Player choices
        choices_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        self.create_retro_label(
            choices_frame,
            text="> CHOOSE YOUR MOVE:",
            font=self.retro_font_large
        ).pack()
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(choices_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        choice_colors = [self.retro_colors["button"], self.retro_colors["accent"], self.retro_colors["accent2"]]
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = self.create_retro_button(
                buttons_frame,
                text=f"> {choice.upper()}",
                command=lambda c=choice: self.make_online_choice(Choice(c)),
                width=120,
                height=40,
                fg_color=choice_colors[i]
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Result display
        self.result_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        
        # Status label
        status_label = self.create_retro_label(
            self.result_frame,
            text="> WAITING FOR OPPONENT'S CHOICE...",
            font=self.retro_font
        )
        status_label.pack(pady=20)
    
    def make_online_choice(self, choice: Choice):
        """Send choice to opponent"""
        self.play_sound("click")
        
        # Send choice to opponent
        if self.network_manager:
            self.network_manager.send_player_choice(choice.value)
        
        # Store our choice and wait for opponent
        self.game.player1_choice = choice
        self.opponent_choice = None
        self.opponent_ready = False
        
        # Show waiting status
        self.update_online_status("Choice sent! Waiting for opponent...")
        
        # Check periodically if opponent has responded
        self.check_opponent_response()
    
    def update_online_status(self, message: str):
        """Update status message in result frame"""
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        status = self.create_retro_label(
            self.result_frame,
            text=f"> {message.upper()}",
            font=self.retro_font
        )
        status.pack(pady=20)
    
    def check_opponent_response(self, attempts: int = 0):
        """Check if opponent has made their choice"""
        if attempts > 30:  # 30 seconds timeout
            self._show_error("Opponent did not respond. Connection may have been lost.")
            self.show_main_menu()
            return
        
        if self.opponent_choice:
            # Both players have chosen, play the round
            self.game.player2_choice = self.opponent_choice
            result, message = self.game.play_round(self.game.player1_choice, self.game.player2_choice)
            self.update_online_game_ui(result, message)
        else:
            # Check again after 1 second
            self.after(1000, lambda: self.check_opponent_response(attempts + 1))
    
    def update_online_game_ui(self, result: GameResult, message: str):
        """Update the online game UI with result"""
        # Update scores safely
        try:
            if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                self.player1_score_label.configure(text=f"SCORE: {self.game.player1_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.configure(text=f"SCORE: {self.game.player2_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'round_label') and self.round_label.winfo_exists():
                self.round_label.configure(text=f"Round {self.game.round}")
        except Exception:
            pass

        # Clear previous result and show new info
        try:
            if hasattr(self, 'result_frame') and self.result_frame.winfo_exists():
                for widget in self.result_frame.winfo_children():
                    widget.destroy()

                # Show choices
                choices_text = f"YOUR MOVE: {self.game.player1_choice.value.upper()} | OPPONENT: {self.game.player2_choice.value.upper()}"
                choices_label = self.create_retro_label(
                    self.result_frame,
                    text=f"> {choices_text}",
                    font=self.retro_font
                )
                choices_label.pack(pady=10)

                # Show result
                result_label = self.create_retro_label(
                    self.result_frame,
                    text=f">>> {message.upper()} <<<",
                    font=self.retro_font_large,
                    text_color=self.retro_colors["accent"]
                )
                result_label.pack(pady=10)

                # Next round button
                next_btn = self.create_retro_button(
                    self.result_frame,
                    text="> NEXT ROUND",
                    command=lambda: [self.play_sound("click"), self.show_online_game_screen()]
                )
                next_btn.pack(pady=10)
        except Exception:
            pass

        # Play appropriate sound
        try:
            if result == GameResult.WIN:
                self.play_sound("win")
            elif result == GameResult.LOSE:
                self.play_sound("lose")
            else:
                self.play_sound("draw")
        except Exception:
            pass
    
    def cancel_online_game(self):
        """Cancel online game and return to main menu"""
        self.play_sound("click")
        if self.network_manager:
            self.network_manager.disconnect()
        self.show_main_menu()
    
    def start_game(self, mode: GameMode):
        """Start a new game with the specified mode"""
        self.play_sound("click")
        self.game.set_game_mode(mode)
        player_name = self.player_name.get() or "Player 1"
        
        if mode == GameMode.VS_AI:
            self.game.set_player_names(player_name, "AI")
        elif mode == GameMode.AI_VS_AI:
            self.game.set_player_names("AI 1", "AI 2")
        
        self.show_game_screen()
    
    def show_game_screen(self):
        """Show the main game screen"""
        self.clear_frame()
        
        # Configure grid
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(1, weight=1)
        
        # Header with scores
        header = ctk.CTkFrame(
            self.current_frame,
            height=60,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        self.create_retro_label(
            player1_frame,
            text=f"> {self.game.player1_name.upper()}",
            font=self.retro_font
        ).pack()
        
        self.player1_score_label = self.create_retro_label(
            player1_frame,
            text=f"SCORE: {self.game.player1_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = self.create_retro_label(
            round_frame,
            text=f">>> ROUND {self.game.round} <<<",
            font=self.retro_font_large,
            text_color=self.retro_colors["accent"]
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        self.create_retro_label(
            player2_frame,
            text=f"{self.game.player2_name.upper()} <",
            font=self.retro_font
        ).pack()
        
        self.player2_score_label = self.create_retro_label(
            player2_frame,
            text=f"SCORE: {self.game.player2_score}",
            text_color=self.retro_colors["text_secondary"]
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(
            self.current_frame,
            fg_color=self.retro_colors["frame"],
            border_color=self.retro_colors["border"],
            border_width=2
        )
        game_area.grid(row=1, column=0, sticky="nsew")
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        # Player choices
        choices_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        self.create_retro_label(
            choices_frame,
            text="> CHOOSE YOUR MOVE:",
            font=self.retro_font_large
        ).pack()
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(choices_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        choice_colors = [self.retro_colors["button"], self.retro_colors["accent"], self.retro_colors["accent2"]]
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = self.create_retro_button(
                buttons_frame,
                text=f"> {choice.upper()}",
                command=lambda c=choice: self.make_choice(Choice(c)),
                width=120,
                height=40,
                fg_color=choice_colors[i]
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Result display
        self.result_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, pady=(20, 0))
        
        restart_btn = self.create_retro_button(
            buttons_frame,
            text="> RESTART",
            command=self.restart_game,
            width=120,
            height=40
        )
        restart_btn.pack(side="left", padx=10)
        
        menu_btn = self.create_retro_button(
            buttons_frame,
            text="> MAIN MENU",
            command=lambda: [self.play_sound("click"), self.show_main_menu()],
            width=120,
            height=40
        )
        menu_btn.pack(side="left", padx=10)
        
        # If in AI vs AI mode, start auto-playing
        if self.game.game_mode == GameMode.AI_VS_AI:
            self.after(1000, self.ai_vs_ai_round)
    
    def make_choice(self, choice: Choice):
        """Handle player's choice"""
        self.play_sound("click")
        
        if self.game.game_mode == GameMode.VS_AI:
            result, message = self.game.play_round(choice)
            self.update_game_ui(result, message)
        elif self.game.game_mode == GameMode.VS_PLAYER:
            # TODO: Implement multiplayer logic
            pass
    
    def ai_vs_ai_round(self):
        """Handle AI vs AI game mode"""
        if self.game.game_mode == GameMode.AI_VS_AI:
            result, message = self.game.play_round()
            self.update_game_ui(result, message)
            
            # Schedule next round
            self.after(2000, self.ai_vs_ai_round)
    
    def update_game_ui(self, result: GameResult, message: str):
        """Update the game UI with the latest result"""
        # Update scores safely (widgets may have been destroyed)
        try:
            if hasattr(self, 'player1_score_label') and self.player1_score_label.winfo_exists():
                self.player1_score_label.configure(text=f"SCORE: {self.game.player1_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.configure(text=f"SCORE: {self.game.player2_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'round_label') and self.round_label.winfo_exists():
                self.round_label.configure(text=f"Round {self.game.round}")
        except Exception:
            pass

        # Clear previous result and show new result if result_frame exists
        try:
            if hasattr(self, 'result_frame') and self.result_frame.winfo_exists():
                for widget in self.result_frame.winfo_children():
                    widget.destroy()

                result_label = self.create_retro_label(
                    self.result_frame,
                    text=f">>> {message.upper()} <<<",
                    font=self.retro_font_large,
                    text_color=self.retro_colors["accent"]
                )
                result_label.pack(pady=20)
        except Exception:
            pass

        # Play appropriate sound
        try:
            if result == GameResult.WIN:
                self.play_sound("win")
            elif result == GameResult.LOSE:
                self.play_sound("lose")
            else:
                self.play_sound("draw")
        except Exception:
            pass
    
    def restart_game(self):
        """Restart the current game"""
        self.play_sound("click")
        self.game.reset_game()
        self.show_game_screen()