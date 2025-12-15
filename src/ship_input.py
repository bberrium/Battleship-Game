# src/ship_input.py
from typing import List, Tuple, Set
from utils import *

def parse_ship_input(input_str: str) -> List[Tuple[int, int]]:
    """Parse ship coordinates from input like 'A1 A2 A3 A4'"""
    coords = []
    parts = input_str.strip().split()
    for part in parts:
        try:
            col = ord(part[0].upper()) - ord('A')
            row = int(part[1:]) - 1
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                coords.append((row, col))
            else:
                return []
        except (ValueError, IndexError):
            return []
    return coords

def validate_ship_shape(coords: List[Tuple[int, int]], expected_size: int) -> bool:
    """Validate ship is a straight horizontal or vertical line of correct size"""
    if len(coords) != expected_size:
        return False
    
    if expected_size == 1:
        return True
    
    # Remove duplicates and sort
    coords = sorted(list(set(coords)))
    
    if len(coords) != expected_size:
        return False
    
    rows = [c[0] for c in coords]
    cols = [c[1] for c in coords]
    
    # Check if horizontal (same row, consecutive columns)
    if len(set(rows)) == 1:
        return cols == list(range(min(cols), max(cols) + 1))
    
    # Check if vertical (same column, consecutive rows)
    if len(set(cols)) == 1:
        return rows == list(range(min(rows), max(rows) + 1))
    
    return False

def display_placement_board(placed_ships: List[List[Tuple[int, int]]]):
    """Display current ship placements"""
    print("\nDEBUG: Entering display_placement_board")
    board = [['~' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    for ship_id, ship in enumerate(placed_ships):
        print(f"DEBUG: Placing ship {ship_id+1} at coordinates {ship}")
        for row, col in ship:
            board[row][col] = str(ship_id + 1)
    
    print("\n  A B C D E F G H I J")
    for i in range(BOARD_SIZE):
        print(f"{i+1:2} " + " ".join(board[i])) #:2 - width 2 characters, right-aligned by default

def get_player_ships() -> List[List[Tuple[int, int]]]:
    """Interactive ship placement with validation"""
    ships = []
    placed_cells = set()
    
    print("\n" + "="*50)
    print("SHIP PLACEMENT")
    print("="*50)
    print("\nBoard coordinates: A-J (columns), 1-10 (rows)")
    print("Input format: A1 A2 A3 (space-separated coordinates)")
    print("\nShip sizes to place:")
    for i, size in enumerate(SHIP_SIZES):
        print(f"  {i+1}. Size {size}")
    print()
    
    for i, size in enumerate(SHIP_SIZES):
        while True:
            if ships:
                display_placement_board(ships)
            
            print(f"\n[{i+1}/{len(SHIP_SIZES)}] Place ship of size {size}:")
            print(f"Enter {size} coordinate(s): ", end="")
            
            try:
                input_str = input()
                
                if input_str.lower() in ['quit', 'exit']:
                    print("Placement cancelled.")
                    return []
                
                coords = parse_ship_input(input_str)
                
                if not coords:
                    print("Invalid input format. Use format like: A1 A2 A3")
                    continue
                
                if not validate_ship_shape(coords, size):
                    print(f"Invalid ship shape. Must be {size} cells in a straight line.")
                    continue
                
                ship_set = set(coords)
                
                # Check for overlap
                if ship_set & placed_cells:
                    print("Ship overlaps with existing ship!")
                    continue
                
                # Check for adjacency
                if ships_touch(ship_set, [set(s) for s in ships]):
                    print("Ships cannot touch each other (even diagonally)!")
                    continue
                
                # Ship is valid
                ships.append(coords)
                placed_cells.update(ship_set)
                print(f"Ship {i+1} placed successfully!")
                break
                
            except KeyboardInterrupt:
                print("\nPlacement cancelled.")
                return []
            except Exception as e:
                print(f"Error: {e}")
    
    display_placement_board(ships)
    print("\nAll ships placed successfully!")
    return ships


