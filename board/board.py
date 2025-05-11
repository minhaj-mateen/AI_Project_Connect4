import numpy as np
import copy

class Board:
    ROW_COUNT = 6
    COLUMN_COUNT = 7

    EMPTY = 0
    PLAYER1_PIECE = 1
    PLAYER2_PIECE = 2

    WINDOW_LENGTH = 4

    PREV_MOVE = None
    PREV_PLAYER = None
    CURR_PLAYER = None

    # Powerup types
    REMOVE_PIECE = 1
    GRAVITY_FLIP = 2
    SWAP_COLOR = 3
    DOUBLE_MOVE = 4

    def __init__(self, current_player):
        self.board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), dtype=int)
        self.num_slots_filled = 0
        self.CURR_PLAYER = current_player
        self.PREV_PLAYER = self.get_opp_player(current_player)
        self.powerups_used = {self.PLAYER1_PIECE: [], self.PLAYER2_PIECE: []}
        self.double_move_available = {self.PLAYER1_PIECE: False, self.PLAYER2_PIECE: False}
        self.double_move_column = {self.PLAYER1_PIECE: None, self.PLAYER2_PIECE: None}

    def copy_board(self):
        c = copy.deepcopy(self)
        return c

    def get_board(self):
        return self.board

    def get_row_col(self, row, col):
        return self.board[row][col]

    def get_opp_player(self, piece):
        if piece == self.PLAYER1_PIECE:
            return self.PLAYER2_PIECE
        else:
            return self.PLAYER1_PIECE

    def drop_piece(self, col, piece):
        row = self.get_next_open_row(col)
        self.board[row][col] = piece
        self.num_slots_filled += 1
        self.PREV_MOVE = col
        self.PREV_PLAYER = piece
        self.CURR_PLAYER = self.get_opp_player(piece)

    def is_valid_location(self, col):
        return self.board[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self, col):
        for r in range(self.ROW_COUNT):
            if self.board[r][col] == 0:
                return r

    def print_board(self):
        print(np.flip(self.board, 0))

    def winning_move(self, piece):
        # Check horizontal locations for win
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True

        # Check positively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True

        # Check negatively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True

    def get_valid_locations(self):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations

    def check_draw(self):
        if self.num_slots_filled == self.ROW_COUNT * self.COLUMN_COUNT:
            return True
        return False

    def search_result(self, piece):
        if self.winning_move(piece):
            return 1
        elif self.winning_move(self.get_opp_player(piece)):
            return 0
        elif not self.get_valid_locations():
            return 0.5

    def remove_piece(self, col, piece):
        """Remove a piece from the specified column and let pieces above fall down"""
        # Check if there are any pieces in the column
        has_pieces = False
        for row in range(self.ROW_COUNT):
            if self.board[row][col] != self.EMPTY:
                has_pieces = True
                break
        
        if not has_pieces:
            return False
        
        # Find the topmost piece in the column
        for row in range(self.ROW_COUNT):
            if self.board[row][col] != self.EMPTY:
                # Remove the piece
                self.board[row][col] = self.EMPTY
                self.num_slots_filled -= 1
                
                # Let pieces above fall down
                for r in range(row + 1, self.ROW_COUNT):
                    if self.board[r][col] != self.EMPTY:
                        self.board[r-1][col] = self.board[r][col]
                        self.board[r][col] = self.EMPTY
                return True
        return False

    def gravity_flip(self, piece):
        """Flip the board vertically and make pieces fall down"""
        # Create a copy of the board
        new_board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), dtype=int)
        
        # For each column, flip the pieces
        for col in range(self.COLUMN_COUNT):
            pieces = []
            # Collect all pieces in the column
            for row in range(self.ROW_COUNT):
                if self.board[row][col] != self.EMPTY:
                    pieces.append(self.board[row][col])
            
            # Place pieces from bottom up
            for i, piece_val in enumerate(pieces):
                new_board[self.ROW_COUNT - 1 - i][col] = piece_val
        
        self.board = new_board
        
        # Make pieces fall down in each column
        for col in range(self.COLUMN_COUNT):
            # Move all pieces down to the bottom
            pieces = []
            for row in range(self.ROW_COUNT):
                if self.board[row][col] != self.EMPTY:
                    pieces.append(self.board[row][col])
            
            # Clear the column
            for row in range(self.ROW_COUNT):
                self.board[row][col] = self.EMPTY
            
            # Place pieces from bottom up
            for i, piece_val in enumerate(pieces):
                self.board[self.ROW_COUNT - 1 - i][col] = piece_val
        
        return True

    def swap_color(self, piece, is_row, index):
        """Swap colors in a row or column"""
        if is_row:
            if 0 <= index < self.ROW_COUNT:
                for col in range(self.COLUMN_COUNT):
                    if self.board[index][col] != self.EMPTY:
                        self.board[index][col] = self.get_opp_player(self.board[index][col])
                return True
        else:
            if 0 <= index < self.COLUMN_COUNT:
                for row in range(self.ROW_COUNT):
                    if self.board[row][index] != self.EMPTY:
                        self.board[row][index] = self.get_opp_player(self.board[row][index])
                return True
        return False

    def enable_double_move(self, piece, col):
        """Enable double move for the next turn"""
        if self.is_valid_location(col):
            self.double_move_available[piece] = True
            self.double_move_column[piece] = col
            return True
        return False

    def use_powerup(self, powerup_type, piece, **kwargs):
        """Use a powerup and track its usage"""
        if powerup_type in self.powerups_used[piece]:
            return False  # Powerup already used
        
        success = False
        if powerup_type == self.REMOVE_PIECE:
            success = self.remove_piece(kwargs.get('col'), piece)
        elif powerup_type == self.GRAVITY_FLIP:
            success = self.gravity_flip(piece)
        elif powerup_type == self.SWAP_COLOR:
            success = self.swap_color(piece, kwargs.get('is_row'), kwargs.get('index'))
        elif powerup_type == self.DOUBLE_MOVE:
            success = self.enable_double_move(piece, kwargs.get('col'))
        
        if success:
            self.powerups_used[piece].append(powerup_type)
        return success

    def get_available_powerups(self, piece):
        """Get list of available powerups for a player"""
        all_powerups = [self.REMOVE_PIECE, self.GRAVITY_FLIP, self.SWAP_COLOR, self.DOUBLE_MOVE]
        return [p for p in all_powerups if p not in self.powerups_used[piece]]
