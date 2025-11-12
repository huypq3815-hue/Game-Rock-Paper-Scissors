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
        
        # Configure window
        self.title("Rock Paper Scissors")
        self.geometry("800x600")
        self.minsize(800, 600)
        
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
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Error loading sounds: {e}")
    
    def play_sound(self, sound_name: str):
        """Play a sound effect if available"""
        if sound_name in self.sounds:
            try:
                pygame.mixer.Sound.play(self.sounds[sound_name])
            except:
                pass
    
    def clear_frame(self):
        """Clear the current frame"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ctk.CTkFrame(self)
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
                text="Rock Paper Scissors",
                font=("Arial", 32, "bold")
            )
            title.pack(pady=(0, 40))
        
        # Player name entry
        name_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        name_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(name_frame, text="Your name:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.player_name = ctk.CTkEntry(name_frame, width=200, placeholder_text="Player")
        self.player_name.pack(side="left")
        
        # Game mode buttons
        button_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        button_frame.pack(expand=True, fill="both", pady=20)
        
        vs_ai_btn = ctk.CTkButton(
            button_frame,
            text="Play vs AI",
            font=("Arial", 16, "bold"),
            height=50,
            command=lambda: self.start_game(GameMode.VS_AI)
        )
        vs_ai_btn.pack(fill="x", pady=10, padx=100)
        
        vs_local_btn = ctk.CTkButton(
            button_frame,
            text="Play Local (2 Players)",
            font=("Arial", 16, "bold"),
            height=50,
            command=lambda: self.show_local_2player_menu()
        )
        vs_local_btn.pack(fill="x", pady=10, padx=100)
        
        vs_player_btn = ctk.CTkButton(
            button_frame,
            text="Play Online",
            font=("Arial", 16, "bold"),
            height=50,
            command=lambda: self.show_online_menu()
        )
        vs_player_btn.pack(fill="x", pady=10, padx=100)
        
        ai_vs_ai_btn = ctk.CTkButton(
            button_frame,
            text="Watch AI vs AI",
            font=("Arial", 16, "bold"),
            height=50,
            command=lambda: self.start_game(GameMode.AI_VS_AI)
        )
        ai_vs_ai_btn.pack(fill="x", pady=10, padx=100)
        
        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            font=("Arial", 14),
            fg_color="#FF5555",
            hover_color="#FF3333",
            height=40,
            command=self.quit
        )
        exit_btn.pack(fill="x", pady=(20, 0), padx=100)
    
    def show_local_2player_menu(self):
        """Show the local 2-player setup menu"""
        self.clear_frame()
        
        title = ctk.CTkLabel(
            self.current_frame,
            text="Local 2-Player Game",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(0, 30))
        
        # Player 1 name
        player1_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        player1_frame.pack(fill="x", pady=10, padx=100)
        
        ctk.CTkLabel(player1_frame, text="Player 1 Name:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.player1_local_name = ctk.CTkEntry(player1_frame, width=200, placeholder_text="Player 1")
        self.player1_local_name.pack(side="left")
        
        # Player 2 name
        player2_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        player2_frame.pack(fill="x", pady=10, padx=100)
        
        ctk.CTkLabel(player2_frame, text="Player 2 Name:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.player2_local_name = ctk.CTkEntry(player2_frame, width=200, placeholder_text="Player 2")
        self.player2_local_name.pack(side="left")
        
        # Start button
        start_btn = ctk.CTkButton(
            self.current_frame,
            text="Start Game",
            font=("Arial", 16, "bold"),
            height=50,
            command=self.start_local_2player_game
        )
        start_btn.pack(fill="x", pady=20, padx=100)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.current_frame,
            text="Back to Main Menu",
            font=("Arial", 14),
            height=40,
            command=self.show_main_menu
        )
        back_btn.pack(pady=(10, 0))
    
    def start_local_2player_game(self):
        """Start a local 2-player game"""
        self.play_sound("click")
        self.game.set_game_mode(GameMode.VS_LOCAL_PLAYER)
        player1_name = self.player1_local_name.get() or "Player 1"
        player2_name = self.player2_local_name.get() or "Player 2"
        self.game.set_player_names(player1_name, player2_name)
        self.show_local_2player_game_screen()

    def show_online_menu(self):
        """Show the online game menu"""
        self.clear_frame()
        
        title = ctk.CTkLabel(
            self.current_frame,
            text="Online Game",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(0, 30))
        
        # Create room button
        create_btn = ctk.CTkButton(
            self.current_frame,
            text="Create Room",
            font=("Arial", 16, "bold"),
            height=50,
            command=self.create_room
        )
        create_btn.pack(fill="x", pady=10, padx=100)
        
        # Join room section
        join_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        join_frame.pack(fill="x", pady=20, padx=100)
        
        self.room_code = ctk.CTkEntry(
            join_frame,
            placeholder_text="Enter Room Code",
            font=("Arial", 14)
        )
        self.room_code.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        join_btn = ctk.CTkButton(
            join_frame,
            text="Join",
            font=("Arial", 14, "bold"),
            width=80,
            command=self.join_room
        )
        join_btn.pack(side="right")
        
        # Back button
        back_btn = ctk.CTkButton(
            self.current_frame,
            text="Back to Main Menu",
            font=("Arial", 14),
            height=40,
            command=self.show_main_menu
        )
        back_btn.pack(pady=(30, 0))
    
    def create_room(self):
        """Create a new online game room"""
        self.play_sound("click")
        
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
        dialog.title("Error")
        dialog.geometry("400x150")
        dialog.grab_set()
        
        label = ctk.CTkLabel(
            dialog,
            text=error_message,
            font=("Arial", 14),
            text_color="#FF6B6B"
        )
        label.pack(pady=20, padx=20)
        
        btn = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        btn.pack(pady=10)
    
    def show_local_2player_game_screen(self):
        """Show the local 2-player game screen with alternating player inputs"""
        self.clear_frame()
        
        # Configure grid
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(1, weight=1)
        
        # Header with scores
        header = ctk.CTkFrame(self.current_frame, height=60)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        ctk.CTkLabel(
            player1_frame,
            text=self.game.player1_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player1_score_label = ctk.CTkLabel(
            player1_frame,
            text=f"Score: {self.game.player1_score}",
            font=("Arial", 14)
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = ctk.CTkLabel(
            round_frame,
            text=f"Round {self.game.round}",
            font=("Arial", 18, "bold")
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        ctk.CTkLabel(
            player2_frame,
            text=self.game.player2_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player2_score_label = ctk.CTkLabel(
            player2_frame,
            text=f"Score: {self.game.player2_score}",
            font=("Arial", 14)
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(self.current_frame)
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
        title = ctk.CTkLabel(
            game_area,
            text=f"{player_name}'s Turn",
            font=("Arial", 24, "bold"),
            text_color="#FFD700"
        )
        title.grid(row=0, column=0, columnspan=3, pady=(20, 10))
        
        # Instruction
        instruction = ctk.CTkLabel(
            game_area,
            text="Choose your move:",
            font=("Arial", 16)
        )
        instruction.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = ctk.CTkButton(
                buttons_frame,
                text=choice.capitalize(),
                font=("Arial", 14, "bold"),
                width=120,
                height=40,
                command=lambda c=choice, p=player_num: self.local_player_choice(c, p)
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Warning message (don't let other player see)
        warning = ctk.CTkLabel(
            game_area,
            text="⚠️ Other player should not look at the screen!",
            font=("Arial", 12),
            text_color="#FF6B6B"
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
        
        waiting = ctk.CTkLabel(
            self.current_frame,
            text="Player 1's choice has been saved!",
            font=("Arial", 20, "bold")
        )
        waiting.pack(pady=(50, 20))
        
        instruction = ctk.CTkLabel(
            self.current_frame,
            text="Give the computer to Player 2 and click Ready",
            font=("Arial", 16)
        )
        instruction.pack(pady=20)
        
        # Get the game area frame to pass to show_local_player_input
        game_area = ctk.CTkFrame(self.current_frame)
        game_area.pack(expand=True, fill="both", padx=20, pady=20)
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        ready_btn = ctk.CTkButton(
            self.current_frame,
            text="Ready - Show Player 2 Input",
            font=("Arial", 16, "bold"),
            height=50,
            command=lambda: self.show_local_player_input(2, game_area)
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
        header = ctk.CTkFrame(self.current_frame, height=60)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        ctk.CTkLabel(
            player1_frame,
            text=self.game.player1_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        ctk.CTkLabel(
            player1_frame,
            text=f"Score: {self.game.player1_score}",
            font=("Arial", 14)
        ).pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        ctk.CTkLabel(
            round_frame,
            text=f"Round {self.game.round - 1}",
            font=("Arial", 18, "bold")
        ).pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        ctk.CTkLabel(
            player2_frame,
            text=self.game.player2_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        ctk.CTkLabel(
            player2_frame,
            text=f"Score: {self.game.player2_score}",
            font=("Arial", 14)
        ).pack()
        
        # Result area
        result_area = ctk.CTkFrame(self.current_frame)
        result_area.grid(row=1, column=0, sticky="nsew")
        result_area.grid_columnconfigure((0, 1, 2), weight=1)
        result_area.grid_rowconfigure(1, weight=1)
        
        # Show choices
        choices_frame = ctk.CTkFrame(result_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=20)
        
        ctk.CTkLabel(
            choices_frame,
            text=f"{self.game.player1_name}: {self.game.player1_choice.value.upper()}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=40)
        
        ctk.CTkLabel(
            choices_frame,
            text="vs",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            choices_frame,
            text=f"{self.game.player2_choice.value.upper()}: {self.game.player2_name}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=40)
        
        # Result message
        result_label = ctk.CTkLabel(
            result_area,
            text=message,
            font=("Arial", 20, "bold"),
            text_color="#FFD700"
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
        
        next_btn = ctk.CTkButton(
            button_frame,
            text="Next Round",
            font=("Arial", 14),
            width=120,
            height=40,
            command=self.show_local_2player_game_screen
        )
        next_btn.pack(side="left", padx=10)
        
        menu_btn = ctk.CTkButton(
            button_frame,
            text="Main Menu",
            font=("Arial", 14),
            width=120,
            height=40,
            command=self.show_main_menu
        )
        menu_btn.pack(side="left", padx=10)
    
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
        dialog.title("Error")
        dialog.geometry("400x150")
        dialog.grab_set()
        
        label = ctk.CTkLabel(
            dialog,
            text=error_message,
            font=("Arial", 14),
            text_color="#FF6B6B"
        )
        label.pack(pady=20, padx=20)
        
        btn = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        btn.pack(pady=10)
    
    def show_waiting_for_opponent(self, room_code: str):
        """Show waiting screen for opponent to join"""
        self.clear_frame()
        
        title = ctk.CTkLabel(
            self.current_frame,
            text="Waiting for Opponent",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(50, 30))
        
        info_label = ctk.CTkLabel(
            self.current_frame,
            text="Share this room code with your opponent:",
            font=("Arial", 14)
        )
        info_label.pack(pady=(0, 10))
        
        # Room code display with copy button
        code_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        code_frame.pack(pady=20)
        
        code_label = ctk.CTkLabel(
            code_frame,
            text=room_code,
            font=("Arial", 18, "bold"),
            text_color="#FFD700"
        )
        code_label.pack(side="left", padx=(0, 10))
        
        copy_btn = ctk.CTkButton(
            code_frame,
            text="Copy",
            font=("Arial", 12),
            width=80,
            command=lambda: self.copy_to_clipboard(room_code)
        )
        copy_btn.pack(side="left")
        
        # Waiting indicator
        waiting_label = ctk.CTkLabel(
            self.current_frame,
            text="⏳ Waiting...",
            font=("Arial", 14),
            text_color="#FFD700"
        )
        waiting_label.pack(pady=(30, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            self.current_frame,
            text="Cancel",
            font=("Arial", 14),
            height=40,
            fg_color="#FF5555",
            hover_color="#FF3333",
            command=self.cancel_online_game
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
        header = ctk.CTkFrame(self.current_frame, height=60)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        ctk.CTkLabel(
            player1_frame,
            text=self.game.player1_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player1_score_label = ctk.CTkLabel(
            player1_frame,
            text=f"Score: {self.game.player1_score}",
            font=("Arial", 14)
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = ctk.CTkLabel(
            round_frame,
            text=f"Round {self.game.round}",
            font=("Arial", 18, "bold")
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        ctk.CTkLabel(
            player2_frame,
            text=self.game.player2_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player2_score_label = ctk.CTkLabel(
            player2_frame,
            text=f"Score: {self.game.player2_score}",
            font=("Arial", 14)
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(self.current_frame)
        game_area.grid(row=1, column=0, sticky="nsew")
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        # Player choices
        choices_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ctk.CTkLabel(
            choices_frame,
            text="Choose your move:",
            font=("Arial", 16)
        ).pack()
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(choices_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = ctk.CTkButton(
                buttons_frame,
                text=choice.capitalize(),
                font=("Arial", 14, "bold"),
                width=120,
                height=40,
                command=lambda c=choice: self.make_online_choice(Choice(c))
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Result display
        self.result_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        
        # Status label
        status_label = ctk.CTkLabel(
            self.result_frame,
            text="Waiting for opponent's choice...",
            font=("Arial", 14)
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
        
        status = ctk.CTkLabel(
            self.result_frame,
            text=message,
            font=("Arial", 14)
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
                self.player1_score_label.configure(text=f"Score: {self.game.player1_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.configure(text=f"Score: {self.game.player2_score}")
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
                choices_text = f"Your move: {self.game.player1_choice.value.upper()} | Opponent: {self.game.player2_choice.value.upper()}"
                choices_label = ctk.CTkLabel(
                    self.result_frame,
                    text=choices_text,
                    font=("Arial", 14)
                )
                choices_label.pack(pady=10)

                # Show result
                result_label = ctk.CTkLabel(
                    self.result_frame,
                    text=message,
                    font=("Arial", 18, "bold"),
                    text_color="#FFD700"
                )
                result_label.pack(pady=10)

                # Next round button
                next_btn = ctk.CTkButton(
                    self.result_frame,
                    text="Next Round",
                    font=("Arial", 14),
                    command=self.show_online_game_screen
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
        header = ctk.CTkFrame(self.current_frame, height=60)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Player 1 info
        player1_frame = ctk.CTkFrame(header, fg_color="transparent")
        player1_frame.grid(row=0, column=0, sticky="w", padx=20)
        
        ctk.CTkLabel(
            player1_frame,
            text=self.game.player1_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player1_score_label = ctk.CTkLabel(
            player1_frame,
            text=f"Score: {self.game.player1_score}",
            font=("Arial", 14)
        )
        self.player1_score_label.pack()
        
        # Round info
        round_frame = ctk.CTkFrame(header, fg_color="transparent")
        round_frame.grid(row=0, column=1)
        
        self.round_label = ctk.CTkLabel(
            round_frame,
            text=f"Round {self.game.round}",
            font=("Arial", 18, "bold")
        )
        self.round_label.pack()
        
        # Player 2 info
        player2_frame = ctk.CTkFrame(header, fg_color="transparent")
        player2_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        ctk.CTkLabel(
            player2_frame,
            text=self.game.player2_name,
            font=("Arial", 16, "bold")
        ).pack()
        
        self.player2_score_label = ctk.CTkLabel(
            player2_frame,
            text=f"Score: {self.game.player2_score}",
            font=("Arial", 14)
        )
        self.player2_score_label.pack()
        
        # Game area
        game_area = ctk.CTkFrame(self.current_frame)
        game_area.grid(row=1, column=0, sticky="nsew")
        game_area.grid_columnconfigure((0, 1, 2), weight=1)
        game_area.grid_rowconfigure(1, weight=1)
        
        # Player choices
        choices_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        choices_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ctk.CTkLabel(
            choices_frame,
            text="Choose your move:",
            font=("Arial", 16)
        ).pack()
        
        # Choice buttons
        buttons_frame = ctk.CTkFrame(choices_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        for i, choice in enumerate(["rock", "paper", "scissors"]):
            btn = ctk.CTkButton(
                buttons_frame,
                text=choice.capitalize(),
                font=("Arial", 14, "bold"),
                width=120,
                height=40,
                command=lambda c=choice: self.make_choice(Choice(c))
            )
            btn.grid(row=0, column=i, padx=10)
        
        # Result display
        self.result_frame = ctk.CTkFrame(game_area, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, pady=(20, 0))
        
        restart_btn = ctk.CTkButton(
            buttons_frame,
            text="Restart",
            font=("Arial", 14),
            width=120,
            height=40,
            command=self.restart_game
        )
        restart_btn.pack(side="left", padx=10)
        
        menu_btn = ctk.CTkButton(
            buttons_frame,
            text="Main Menu",
            font=("Arial", 14),
            width=120,
            height=40,
            command=self.show_main_menu
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
                self.player1_score_label.configure(text=f"Score: {self.game.player1_score}")
        except Exception:
            pass

        try:
            if hasattr(self, 'player2_score_label') and self.player2_score_label.winfo_exists():
                self.player2_score_label.configure(text=f"Score: {self.game.player2_score}")
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

                result_label = ctk.CTkLabel(
                    self.result_frame,
                    text=message,
                    font=("Arial", 18, "bold")
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
