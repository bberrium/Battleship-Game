import csv
from typing import List, Tuple, Set

BOARD_SIZE = 10
SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


def get_adjacent_cells(row: int, col: int, include_diagonal: bool = True) -> List[Tuple[int, int]]:
    """Get adjacent cells (8 directions if include_diagonal=True, 4 if False)"""
    adjacent = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] if include_diagonal else [(-1, 0), (0, -1), (0, 1), (1, 0)]
    
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            adjacent.append((r, c))
    return adjacent

def get_surrounding_cells(ship_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Get all cells surrounding a ship (for marking as miss when ship sinks)"""
    surrounding = set()
    for cell in ship_cells:
        surrounding.update(get_adjacent_cells(cell[0], cell[1], include_diagonal=True))
    return surrounding - ship_cells

def ships_touch(ship_cells: Set[Tuple[int, int]], all_ships: List[Set[Tuple[int, int]]]) -> bool:
    """Check if ship touches any existing ships (including diagonally)"""
    for ship in all_ships:
        for cell in ship_cells:
            for adj in get_adjacent_cells(cell[0], cell[1], include_diagonal=True):
                if adj in ship:
                    return True
    return False

def save_ships_to_csv(ships: List[List[Tuple[int, int]]], filename: str):
    """Save ship positions to CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ship_id', 'size', 'row', 'col'])
        for ship_id, ship in enumerate(ships):
            for row, col in ship:
                writer.writerow([ship_id, len(ship), row, col])

def load_ships_from_csv(filename: str) -> List[Set[Tuple[int, int]]]:
    """Load ship positions from CSV"""
    ships = {}
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ship_id = int(row['ship_id'])
            if ship_id not in ships:
                ships[ship_id] = set()
            ships[ship_id].add((int(row['row']), int(row['col'])))
    return [ships[i] for i in sorted(ships.keys())]

def coord_to_str(row: int, col: int) -> str:
    """Convert (row, col) to chess notation like 'A1'"""
    return f"{chr(ord('A') + col)}{row + 1}"

def str_to_coord(s: str) -> Tuple[int, int]:
    """Convert chess notation like 'A1' to (row, col)"""
    col = ord(s[0].upper()) - ord('A')
    row = int(s[1:]) - 1
    return (row, col)