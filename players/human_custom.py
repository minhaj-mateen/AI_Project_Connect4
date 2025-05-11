from board.board import Board

class HumanCustom:
    def __init__(self, piece):
        self.name = "Human (Custom)"
        self.piece = piece
        self.selected_powerup = None
        self.waiting_for_column = False
        self.waiting_for_row_col = False
        self.is_row = None
        self.powerup_params = {}

    def get_move(self, board):
        """Get move from human player using CLI"""
        valid_locations = board.get_valid_locations()
        available_powerups = board.get_available_powerups(board.CURR_PLAYER)
        
        # Check if we're in a double move state
        if board.double_move_available[board.CURR_PLAYER]:
            print("\nDouble Move Active - Must use the same column")
            col = board.double_move_column[board.CURR_PLAYER]
            print(f"Required column: {col}")
            return col
        
        while True:
            print("\nAvailable moves:")
            print("1. Regular Move")
            
            # Display available powerups
            if available_powerups:
                print("\nAvailable powerups:")
                for i, powerup in enumerate(available_powerups, 2):
                    if powerup == Board.REMOVE_PIECE:
                        print(f"{i}. Remove Piece")
                    elif powerup == Board.GRAVITY_FLIP:
                        print(f"{i}. Gravity Flip")
                    elif powerup == Board.SWAP_COLOR:
                        print(f"{i}. Swap Color")
                    elif powerup == Board.DOUBLE_MOVE:
                        print(f"{i}. Double Move")

            try:
                choice = int(input("\nEnter your choice (number): "))
                
                # Handle regular move
                if choice == 1:
                    col = self.get_column_input(board, valid_locations)
                    if col is not None:
                        return col
                
                # Handle powerup
                elif 2 <= choice <= len(available_powerups) + 1:
                    powerup = available_powerups[choice - 2]
                    self.selected_powerup = powerup
                    
                    if powerup == Board.GRAVITY_FLIP:
                        return ('powerup', powerup, {})
                    elif powerup == Board.SWAP_COLOR:
                        is_row = self.get_row_col_choice()
                        if is_row is not None:
                            index = self.get_row_col_index(board, is_row)
                            if index is not None:
                                return ('powerup', powerup, {'is_row': is_row, 'index': index})
                    else:  # REMOVE_PIECE or DOUBLE_MOVE
                        col = self.get_column_input(board, valid_locations)
                        if col is not None:
                            return ('powerup', powerup, {'col': col})
                
                else:
                    print("Invalid choice. Please try again.")
            
            except ValueError:
                print("Please enter a valid number.")

    def get_column_input(self, board, valid_locations):
        """Get column input from player"""
        while True:
            try:
                col = int(input(f"Enter column (0-{Board.COLUMN_COUNT-1}): "))
                if 0 <= col < Board.COLUMN_COUNT:
                    if self.selected_powerup is None:
                        if col in valid_locations:
                            return col
                        else:
                            print("Invalid column. Please try again.")
                    else:
                        if self.selected_powerup == Board.REMOVE_PIECE:
                            if not board.is_valid_location(col):
                                return col
                            else:
                                print("Invalid column for remove piece. Please try again.")
                        elif self.selected_powerup == Board.DOUBLE_MOVE:
                            if col in valid_locations:
                                return col
                            else:
                                print("Invalid column. Please try again.")
                else:
                    print(f"Column must be between 0 and {Board.COLUMN_COUNT-1}")
            except ValueError:
                print("Please enter a valid number.")

    def get_row_col_choice(self):
        """Get row/column choice for color swap"""
        while True:
            choice = input("Choose row or column (r/c): ").lower()
            if choice == 'r':
                return True
            elif choice == 'c':
                return False
            else:
                print("Please enter 'r' for row or 'c' for column.")

    def get_row_col_index(self, board, is_row):
        """Get row/column index for color swap"""
        while True:
            try:
                if is_row:
                    index = int(input(f"Enter row (0-{Board.ROW_COUNT-1}): "))
                    if 0 <= index < Board.ROW_COUNT:
                        return index
                    else:
                        print(f"Row must be between 0 and {Board.ROW_COUNT-1}")
                else:
                    index = int(input(f"Enter column (0-{Board.COLUMN_COUNT-1}): "))
                    if 0 <= index < Board.COLUMN_COUNT:
                        return index
                    else:
                        print(f"Column must be between 0 and {Board.COLUMN_COUNT-1}")
            except ValueError:
                print("Please enter a valid number.") 