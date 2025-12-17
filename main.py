import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ship_input import get_player_ships
from src.bot_generation import generate_bot_ships
from src.gameplay import GameState
from src.utils import save_ships_to_csv, coord_to_str, str_to_coord, BOARD_SIZE

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear') #nt - windows

def setup_game():
    """Setup phase: get ship placements"""
    print("\n" + "="*50)
    print("BATTLESHIP GAME")
    print("="*50)
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Player ship placement
    print("\nPhase 1: Place your ships")
    player_ships = get_player_ships()
    
    if not player_ships:
        print("Ship placement cancelled.")
        return None, None
    
    save_ships_to_csv(player_ships, 'data/player_ships.csv')
    print("Player ships saved to data/player_ships.csv")
    
    # Bot ship generation
    print("\nPhase 2: Generating bot ships...")
    bot_ships = generate_bot_ships()
    save_ships_to_csv(bot_ships, 'data/bot_ships.csv')
    print("Bot ships generated and saved to data/bot_ships.csv")
    
    return player_ships, bot_ships

def get_player_move(game_state: GameState) -> tuple:
    """Get player's move input"""
    while True:
        try:
            print("\nYour turn!")
            move_str = input("Enter coordinates to attack (e.g., A1): ").strip().upper()
            
            if move_str in ['QUIT', 'EXIT']:
                return None
            
            coord = str_to_coord(move_str)
            
            if not (0 <= coord[0] < BOARD_SIZE and 0 <= coord[1] < BOARD_SIZE):
                print("Coordinates out of bounds!")
                continue
            
            if not game_state.is_valid_move(coord, True):
                print("You already tried that coordinate!")
                continue
            
            return coord
            
        except (ValueError, IndexError):
            print("Invalid format! Use format like: A1")
        except Exception as e:
            print(f"Error: {e}")

def play_game(player_ships, bot_ships):
    """Main game loop"""
    game_state = GameState(player_ships, bot_ships)
    
    # Initialize game state CSV
    if os.path.exists('data/game_state.csv'):
        os.remove('data/game_state.csv')
    
    print("\n" + "="*50)
    print("GAME START!")
    print("="*50)
    
    while True:
        game_state.turn += 1
        move_info = {}
        
        # Display current board state
        game_state.display_boards()
        
        print(f"\n--- Turn {game_state.turn} ---")
        
        # Player's turn
        player_coord = get_player_move(game_state)
        
        if player_coord is None:
            print("\nGame ended by player.")
            break
        
        player_hit, player_destroyed = game_state.process_move(player_coord, True)
        
        move_info['player_move'] = coord_to_str(player_coord[0], player_coord[1])
        
        if player_destroyed:
            print(f"\nHIT! You destroyed an enemy ship at {move_info['player_move']}!")
            move_info['player_result'] = "HIT+DESTROYED"
        elif player_hit:
            print(f"\nHIT at {move_info['player_move']}!")
            move_info['player_result'] = "HIT"
        else:
            print(f"\nMISS at {move_info['player_move']}")
            move_info['player_result'] = "MISS"
        
        # Check if player won
        game_over, winner = game_state.is_game_over()
        if game_over:
            game_state.display_boards()
            print("\n" + "="*50)
            print("CONGRATULATIONS! YOU WON!")
            print("="*50)
            game_state.save_state_to_csv('data/game_state.csv', move_info)
            break
        
        # Bot's turn
        print("\nBot is thinking...")
        bot_coord = game_state.get_bot_move()
        bot_hit, bot_destroyed = game_state.process_move(bot_coord, False)
        
        # Update bot AI state
        game_state.update_bot_state(bot_coord, bot_hit, bot_destroyed)
        
        move_info['bot_move'] = coord_to_str(bot_coord[0], bot_coord[1])
        
        if bot_destroyed:
            print(f"Bot HIT and DESTROYED your ship at {move_info['bot_move']}!")
            move_info['bot_result'] = "HIT+DESTROYED"
        elif bot_hit:
            print(f"Bot HIT your ship at {move_info['bot_move']}!")
            move_info['bot_result'] = "HIT"
        else:
            print(f"Bot MISSED at {move_info['bot_move']}")
            move_info['bot_result'] = "MISS"
        
        # Save state
        game_state.save_state_to_csv('data/game_state.csv', move_info)
        
        # Check if bot won
        game_over, winner = game_state.is_game_over()
        if game_over:
            game_state.display_boards()
            print("\n" + "="*50)
            print("GAME OVER - BOT WINS :(")
            print("="*50)
            break
        
        input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    try:
        # Setup phase
        player_ships, bot_ships = setup_game()
        
        if player_ships is None:
            return
        
        input("\nPress Enter to start the game...")
        clear_screen()
        
        # Play phase
        play_game(player_ships, bot_ships)
        
        print("\n" + "="*50)
        print("GAME STATISTICS")
        print("="*50)
        print(f"Game log saved to: data/game_state.csv")
        print(f"Total turns: {open('data/game_state.csv').read().count('\\n') - 1}")
        print("\nThank you for playing Battleship!")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc() #print detailed information about exceptions that occur during program execution

if __name__ == "__main__":
    main()