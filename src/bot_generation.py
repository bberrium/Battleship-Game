import random
from typing import List, Tuple, Set
from src.utils import *

def generate_bot_ships() -> List[List[Tuple[int, int]]]:
    """Generate random valid ship placement for the bot"""
    max_attempts = 10000
    
    placed_cells = set()
    ships = []
    
    for size in SHIP_SIZES:
        ship_placed = False
        
        for _ in range(1000):
            # Random orientation
            horizontal = random.choice([True, False])
            
            if horizontal:
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - size)
                coords = [(row, col + i) for i in range(size)]
            else:
                row = random.randint(0, BOARD_SIZE - size)
                col = random.randint(0, BOARD_SIZE - 1)
                coords = [(row + i, col) for i in range(size)]
            
            ship_set = set(coords)
            
            # Check if placement is valid
            if (ship_set & placed_cells) or ships_touch(ship_set, [set(s) for s in ships]):
                continue
            
            # Valid placement found
            ships.append(coords)
            placed_cells.update(ship_set)
            ship_placed = True
            break
        
        if not ship_placed:
            # Failed to place this ship, restart
            return generate_bot_ships()
    
    return ships

def test_generation():
    """Test bot ship generation"""
    print("Testing bot ship generation...")
    for i in range(5):
        ships = generate_bot_ships()
        print(f"Test {i+1}: Generated {len(ships)} ships")
        
        # Verify no touching
        all_cells = set()
        for ship in ships:
            ship_set = set(ship)
            if ship_set & all_cells:
                print("ERROR: Overlapping ships!")
                return False
            all_cells.update(ship_set)
        
        # Check adjacency
        for i, ship1 in enumerate(ships):
            for j, ship2 in enumerate(ships):
                if i != j and ships_touch(set(ship1), [set(ship2)]):
                    print("ERROR: Ships touching!")
                    return False
    
    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_generation()