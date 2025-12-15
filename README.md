# Battleship Game

A terminal-based implementation of the classic Battleship game with an intelligent bot opponent.

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd battleship
```

2. Install dependencies (none required - uses Python standard library only):
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

## Project Structure

```
battleship/
├── main.py                 # Entry point
├── data/
│   ├── player_ships.csv   # Player ship positions
│   ├── bot_ships.csv      # Bot ship positions
│   └── game_state.csv     # Move-by-move game log
├── src/
│   ├── __init__.py        # Package initializer
│   ├── ship_input.py      # Player ship placement
│   ├── bot_generation.py  # Bot ship generation
│   ├── gameplay.py        # Game logic and bot AI
│   └── utils.py           # Utility functions
├── outputs/
│   └── (game logs)
├── requirements.txt
└── README.md
```

## How to Play

### Ship Placement

When the game starts, you'll be asked to place your ships on a 10×10 grid:

**Input Format:** Use chess-style notation (e.g., `A1 A2 A3 A4`)
- Columns: A-J
- Rows: 1-10

**Ship Configuration:**
- 1 ship of size 4
- 2 ships of size 3
- 3 ships of size 2
- 4 ships of size 1

**Rules:**
- Ships must be placed in straight lines (horizontal or vertical)
- Ships cannot overlap
- Ships cannot touch each other, even diagonally
- All coordinates must be within the board

### Gameplay

**Making Moves:**
- Enter coordinates to attack (e.g., `A5`)
- The board shows:
  - `S` = Your ship
  - `X` = Hit
  - `·` = Miss
  - `~` = Unknown/Water

**Board Display:**
- **Left side:** Your board (shows your ships and enemy attacks)
- **Right side:** Enemy board (shows your attacks)

**Winning Condition:**
- Destroy all enemy ships to win
- If the bot destroys all your ships, you lose

## Input Format

### Ship Placement Input

Ships are entered as space-separated coordinates in chess notation:

**Examples:**
- Size 4 ship (horizontal): `A1 B1 C1 D1`
- Size 3 ship (vertical): `E5 E6 E7`
- Size 2 ship: `H2 H3`
- Size 1 ship: `J10`

The system validates:
1. Correct number of coordinates for ship size
2. Coordinates form a straight line
3. No overlap with existing ships
4. No adjacency (including diagonal) to other ships
5. All coordinates within board bounds

### Attack Input

During gameplay, enter a single coordinate:
- Format: `A1`, `B5`, `J10`, etc.
- Invalid coordinates or already-tried cells will be rejected

## Validation Rules

### Ship Placement Validation

1. **Size Check:** Each ship must have exactly the required number of cells
2. **Shape Check:** Ships must form straight horizontal or vertical lines
3. **Boundary Check:** All coordinates must be within A-J and 1-10
4. **Overlap Check:** Ships cannot share cells
5. **Adjacency Check:** Ships cannot touch, even diagonally

### Move Validation

1. Coordinates must be within board bounds
2. Cannot attack the same cell twice
3. Format must be valid (letter + number)

## Game State Tracking

### CSV Format (data/game_state.csv)

The game maintains a detailed log of all moves:

```csv
turn,player_move,player_result,bot_move,bot_result,player_ships_remaining,bot_ships_remaining
1,A5,MISS,B3,HIT,10,10
2,C7,HIT,B4,HIT,10,10
3,C8,HIT+DESTROYED,B5,MISS,10,9
```

**Columns:**
- `turn`: Turn number
- `player_move`: Player's attack coordinate
- `player_result`: HIT, MISS, or HIT+DESTROYED
- `bot_move`: Bot's attack coordinate
- `bot_result`: HIT, MISS, or HIT+DESTROYED
- `player_ships_remaining`: Player ships still afloat
- `bot_ships_remaining`: Bot ships still afloat

### Ship Position Format (player_ships.csv, bot_ships.csv)

```csv
ship_id,size,row,col
0,4,0,0
0,4,0,1
0,4,0,2
0,4,0,3
1,3,2,5
...
```

Each row represents one cell of a ship, with `ship_id` grouping cells belonging to the same ship.

## Bot AI Logic

The bot implements a three-stage intelligent targeting system:

### 1. Random Shooting Mode
- Initially, the bot selects random untested cells
- Returns to this mode after destroying a ship

### 2. Adjacent Search (First Hit)
- When bot hits a ship (size > 1), it enters target mode
- Tries all 4 adjacent cells (up, down, left, right)
- Randomly selects from valid adjacent cells

### 3. Axis Locking (Second Hit)
- After a second consecutive hit on the same ship (size > 2)
- Determines orientation (horizontal or vertical)
- Continues along the detected axis in both directions
- Searches until hitting misses or board boundaries

### 4. Ship Destruction Handling
- When a ship is destroyed:
  - All surrounding cells (8 directions) are automatically marked as miss
  - Bot returns to random shooting mode
  - These marks are reflected in the CSV and on the board

**Smart Features:**
- Avoids already-tried cells
- Respects board boundaries
- Efficiently eliminates ships once located
- Adapts strategy based on hit patterns

## Display Features

### Board Visualization

The game displays two boards side by side after each move:

```
     YOUR BOARD              ENEMY BOARD
  A B C D E F G H I J     A B C D E F G H I J
 1 S S S S ~ ~ ~ ~ ~ ~    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
 2 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    ~ · ~ ~ ~ ~ ~ ~ ~ ~
 3 ~ ~ S ~ ~ ~ ~ ~ ~ ~    ~ · X X · ~ ~ ~ ~ ~
...
```

**Legend:**
- `S` = Your ship
- `X` = Hit
- `·` = Miss
- `~` = Water/Unknown

### Move Feedback

After each move, the game provides clear feedback:
- `HIT!` - Successful hit
- `HIT! You destroyed an enemy ship!` - Ship destroyed
- `MISS` - Missed attack

## Design Decisions

### CSV-Based State Management
- **Why:** Requirement specified, provides persistent audit trail
- **Benefit:** Easy to analyze game progression post-game
- **Trade-off:** Slightly slower than in-memory, but negligible for this scale

### Chess Notation for Coordinates
- **Why:** Intuitive and familiar to most users
- **Format:** Letter (A-J) + Number (1-10)
- **Alternative considered:** (row, col) tuples - less user-friendly

### Smart Bot AI
- **Progression:** Random → Adjacent → Axis-locked
- **Why:** Balances challenge with fairness
- **Trade-off:** Not unbeatable, but plays intelligently

### Terminal-Based Interface
- **Why:** Requirement specified, cross-platform compatible
- **Benefit:** No GUI dependencies, fast development
- **Enhancement possible:** Could add colors with colorama library

### Ship Placement Method
- **Interactive entry:** User types coordinates for each ship
- **Validation:** Real-time feedback during placement
- **Alternative considered:** File upload - less interactive

### Automatic Surrounding Cell Marking
- **When:** Ship is completely destroyed
- **What:** All 8 surrounding cells marked as miss
- **Why:** Matches real Battleship rules, improves gameplay flow
- **Implementation:** Done automatically in game logic and reflected in CSV

## Testing

The project includes basic testing capabilities:

```bash
# Test bot ship generation
python -m src.bot_generation
```
