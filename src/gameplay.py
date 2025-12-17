import csv
import random
from typing import List, Set, Tuple, Optional
from src.utils import *

class GameState:
    def __init__(self, player_ships: List[List[Tuple[int, int]]], bot_ships: List[List[Tuple[int, int]]]):
        # Convert to sets for easier checking
        self.player_ships = [set(ship) for ship in player_ships]
        self.bot_ships = [set(ship) for ship in bot_ships]
        
        # Track hits and misses
        self.player_hits = set()
        self.player_misses = set()
        self.bot_hits = set()
        self.bot_misses = set()
        
        # Track destroyed ships
        self.player_destroyed = [False] * len(player_ships)
        self.bot_destroyed = [False] * len(bot_ships)
        
        self.turn = 0
        
        # Bot AI state
        self.bot_target_mode = False
        self.bot_current_target = []  # List of hits on current ship
        self.bot_direction = None  # 'horizontal' or 'vertical'
        self.bot_tried_cells = set()
    
    def display_boards(self):
        """Display both boards side by side"""
        print("\n" + "="*55)
        print("       YOUR BOARD                 ENEMY BOARD")
        print("   A B C D E F G H I J        A B C D E F G H I J")
        
        for row in range(BOARD_SIZE):
            # Player board (showing your ships and enemy hits)
            line = f"{row+1:2} "
            for col in range(BOARD_SIZE):
                cell = (row, col)
                if cell in self.bot_hits:
                    line += "X "  # Enemy hit your ship
                elif cell in self.bot_misses:
                    line += "· "  # Enemy missed
                elif any(cell in ship for ship in self.player_ships):
                    line += "S "  # Your ship
                else:
                    line += "~ "  # Water
            
            # Enemy board (showing your hits)
            line += "    "
            line += f"{row+1:2} "
            for col in range(BOARD_SIZE):
                cell = (row, col)
                if cell in self.player_hits:
                    line += "X "  # You hit enemy ship
                elif cell in self.player_misses:
                    line += "· "  # You missed
                else:
                    line += "~ "  # Unknown
            
            print(line)
        
        print("="*55)
        print("Legend: S=Ship X=Hit ·=Miss ~=Water/Unknown")
    
    def is_valid_move(self, coord: Tuple[int, int], is_player: bool) -> bool:
        """Check if a move is valid (not already tried)"""
        if is_player:
            return coord not in self.player_hits and coord not in self.player_misses
        else:
            return coord not in self.bot_hits and coord not in self.bot_misses
    
    def process_move(self, coord: Tuple[int, int], is_player: bool) -> Tuple[bool, bool]:
        """
        Process a move and return (is_hit, ship_destroyed)
        
        This function takes a coordinate and a boolean indicating if the move is made by the player or the bot.
        It checks if the move is a hit, and if so, if the ship is destroyed.
        If the ship is destroyed, it marks all surrounding cells as misses.
        """
        if is_player:
            # Player shoots at bot
            # Check if the move is a hit
            for i, ship in enumerate(self.bot_ships):
                if coord in ship:
                    self.player_hits.add(coord)
                    # Check if ship is destroyed
                    if ship.issubset(self.player_hits) and not self.bot_destroyed[i]: # (true, false) -> ship hit and not destroyed
                        self.bot_destroyed[i] = True
                        self._mark_surrounding_as_miss(ship, True)
                        return True, True # (hit, destroyed)
                    return True, False # (hit, not destroyed)
            # If the move was not a hit, mark it as a miss
            self.player_misses.add(coord)
            # Return that the move was not a hit
            return False, False # (not hit, not destroyed)
        else:
            # Bot shoots at player
            # Check if the move is a hit
            for i, ship in enumerate(self.player_ships):
                if coord in ship:
                    self.bot_hits.add(coord)
                    # Check if ship is destroyed
                    if ship.issubset(self.bot_hits) and not self.player_destroyed[i]:
                        self.player_destroyed[i] = True
                        self._mark_surrounding_as_miss(ship, False)
                        return True, True
                    return True, False
                
            self.bot_misses.add(coord)
            return False, False
    
    def _mark_surrounding_as_miss(self, ship: Set[Tuple[int, int]], is_player: bool):
        """Mark all surrounding cells as miss when a ship is destroyed"""
        surrounding = get_surrounding_cells(ship)
        if is_player:
            self.player_misses.update(surrounding - self.player_hits)
        else:
            self.bot_misses.update(surrounding - self.bot_hits)
    
    def get_bot_move(self) -> Tuple[int, int]:
        """Get bot's next move using AI"""
        
        # If in target mode (hit a ship but not destroyed)
        if self.bot_target_mode and self.bot_current_target:
            move = self._get_smart_target_move()
            if move:
                return move
        
        # Random mode or fallback
        return self._get_random_move()
    
    def _get_smart_target_move(self) -> Optional[Tuple[int, int]]: # only return (int, int) as the next move, or None if no valid move is found
        """Get next move when targeting a ship"""
        
        if len(self.bot_current_target) == 1:
            # Only one hit, try all 4 adjacent cells
            row, col = self.bot_current_target[0]
            candidates = get_adjacent_cells(row, col, include_diagonal=False)
            random.shuffle(candidates)
            
            for cell in candidates:
                if self.is_valid_move(cell, False):
                    return cell
        
        elif len(self.bot_current_target) >= 2:
            # Two or more hits, determine direction
            sorted_targets = sorted(self.bot_current_target)
            
            # Check if horizontal or vertical
            rows = [t[0] for t in sorted_targets]
            cols = [t[1] for t in sorted_targets]
            
            if len(set(rows)) == 1:
                # Horizontal ship
                min_col = min(cols)
                max_col = max(cols)
                
                # Try extending in both directions
                candidates = [
                    (rows[0], min_col - 1),
                    (rows[0], max_col + 1)
                ]
            else:
                # Vertical ship
                min_row = min(rows)
                max_row = max(rows)
                
                candidates = [
                    (min_row - 1, cols[0]),
                    (max_row + 1, cols[0])
                ]
            
            random.shuffle(candidates)
            for cell in candidates:
                if (0 <= cell[0] < BOARD_SIZE and 
                    0 <= cell[1] < BOARD_SIZE and 
                    self.is_valid_move(cell, False)):
                    return cell
        
        return None
    
    def _get_random_move(self) -> Tuple[int, int]:
        """Get a random valid move"""
        attempts = 0
        while attempts < 1000:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            if self.is_valid_move((row, col), False):
                return (row, col)
            attempts += 1
        
        # Fallback: find any valid cell
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move((row, col), False):
                    return (row, col)
        
        raise Exception("No valid moves available")
    
    def update_bot_state(self, coord: Tuple[int, int], is_hit: bool, ship_destroyed: bool):
        """Update bot AI state after a move"""
        if is_hit:
            self.bot_current_target.append(coord)
            self.bot_target_mode = True
            
            if ship_destroyed:
                # Ship destroyed, return to random mode
                self.bot_target_mode = False
                self.bot_current_target = []
                self.bot_direction = None
        else:
            # Miss - continue targeting if still have targets
            if not self.bot_current_target:
                self.bot_target_mode = False
    
    def is_game_over(self) -> Tuple[bool, Optional[str]]:
        """Check if game is over and return winner"""


        if all(self.bot_destroyed):
            return True, "player"
        if all(self.player_destroyed):
            return True, "bot"
        return False, None
    
    def save_state_to_csv(self, filename: str, last_move_info: dict = None):
        """Save current game state to CSV"""
        file_exists = False
        try:
            with open(filename, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass
        
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow([
                    'turn', 'player_move', 'player_result', 
                    'bot_move', 'bot_result',
                    'player_ships_remaining', 'bot_ships_remaining'
                ])
            
            if last_move_info:
                writer.writerow([
                    self.turn,
                    last_move_info.get('player_move', ''),
                    last_move_info.get('player_result', ''),
                    last_move_info.get('bot_move', ''),
                    last_move_info.get('bot_result', ''),
                    sum(1 for x in self.player_destroyed if not x), #the number of destroyed ships for the player
                    sum(1 for x in self.bot_destroyed if not x) #the number of destroyed ships for the bot
                ])

