import numpy as np
from board.board import Board

class MinimaxCustom:
    def __init__(self, depth=4):
        self.depth = depth
        self.powerup_weights = {
            Board.REMOVE_PIECE: 5,    # Removing a piece can be very strategic
            Board.GRAVITY_FLIP: 6,    # Gravity flip can completely change the game state
            Board.SWAP_COLOR: 4,      # Color swap can be powerful in certain situations
            Board.DOUBLE_MOVE: 8      # Double move gives an extra turn
        }

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = Board.PLAYER1_PIECE if piece == Board.PLAYER2_PIECE else Board.PLAYER2_PIECE

        # Prioritize winning moves
        if window.count(piece) == 4:
            score += 10000
        # Prioritize blocking opponent's winning moves
        elif window.count(opp_piece) == 3 and window.count(Board.EMPTY) == 1:
            score -= 5000
        # Prioritize creating winning opportunities
        elif window.count(piece) == 3 and window.count(Board.EMPTY) == 1:
            score += 500
        # Prioritize blocking opponent's opportunities
        elif window.count(opp_piece) == 2 and window.count(Board.EMPTY) == 2:
            score -= 250
        # Encourage building up pieces
        elif window.count(piece) == 2 and window.count(Board.EMPTY) == 2:
            score += 100

        return score

    def score_position(self, board, piece):
        score = 0
        board_array = board.get_board()

        # Score center column (more weight)
        center_array = [int(i) for i in list(board_array[:, Board.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 10

        # Score Horizontal
        for r in range(Board.ROW_COUNT):
            row_array = [int(i) for i in list(board_array[r,:])]
            for c in range(Board.COLUMN_COUNT-3):
                window = row_array[c:c+Board.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(Board.COLUMN_COUNT):
            col_array = [int(i) for i in list(board_array[:,c])]
            for r in range(Board.ROW_COUNT-3):
                window = col_array[r:r+Board.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(Board.ROW_COUNT-3):
            for c in range(Board.COLUMN_COUNT-3):
                window = [board_array[r+i][c+i] for i in range(Board.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Score negative sloped diagonal
        for r in range(Board.ROW_COUNT-3):
            for c in range(Board.COLUMN_COUNT-3):
                window = [board_array[r+3-i][c+i] for i in range(Board.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def evaluate_powerup(self, board, powerup_type, piece, **kwargs):
        """Evaluate the potential impact of using a powerup"""
        # Create a copy of the board to simulate the powerup
        board_copy = board.copy_board()
        original_score = self.score_position(board_copy, piece)
        
        # Apply the powerup
        success = board_copy.use_powerup(powerup_type, piece, **kwargs)
        if not success:
            return float('-inf') if piece == board.PLAYER1_PIECE else float('inf')
        
        # For swap color, we need to evaluate the board after the opponent's move
        if powerup_type == Board.SWAP_COLOR:
            # Only consider swapping if it improves our position
            new_score = self.score_position(board_copy, piece)
            if new_score <= original_score:
                return float('-inf') if piece == board.PLAYER1_PIECE else float('inf')
            
            # Simulate opponent's move
            valid_locations = board_copy.get_valid_locations()
            if valid_locations:
                # Find the best move for the opponent
                opp_piece = board_copy.get_opp_player(piece)
                best_score = float('-inf') if opp_piece == board.PLAYER1_PIECE else float('inf')
                for col in valid_locations:
                    board_copy.drop_piece(col, opp_piece)
                    score = self.score_position(board_copy, piece)
                    if (opp_piece == board.PLAYER1_PIECE and score > best_score) or \
                       (opp_piece == board.PLAYER2_PIECE and score < best_score):
                        best_score = score
                    # Undo the move
                    board_copy.undo_move(col)
                new_score = best_score
        elif powerup_type == Board.DOUBLE_MOVE:
            # For double move, simulate both drops and evaluate
            col = kwargs.get('col')
            if col is not None and board_copy.is_valid_location(col):
                board_copy.drop_piece(col, piece)
                if board_copy.is_valid_location(col):
                    board_copy.drop_piece(col, piece)
                    new_score = self.score_position(board_copy, piece)
                else:
                    new_score = self.score_position(board_copy, piece)
            else:
                return float('-inf') if piece == board.PLAYER1_PIECE else float('inf')
        else:
            new_score = self.score_position(board_copy, piece)
        
        # Calculate the score difference and apply the powerup weight
        score_diff = new_score - original_score
        return score_diff * self.powerup_weights[powerup_type]

    def get_valid_powerup_moves(self, board, piece):
        """Get all valid powerup moves"""
        valid_moves = []
        available_powerups = board.get_available_powerups(piece)
        
        # Don't use powerups if the board is empty
        if all(cell == Board.EMPTY for row in board.get_board() for cell in row):
            return valid_moves
        
        # Limit the number of powerup evaluations to prevent excessive computation
        max_evaluations = 5  # Reduced from 10 to 5
        evaluations = 0
        
        for powerup in available_powerups:
            if evaluations >= max_evaluations:
                break
                
            if powerup == Board.REMOVE_PIECE:
                # Try removing a piece from each column
                for col in range(Board.COLUMN_COUNT):
                    if evaluations >= max_evaluations:
                        break
                    if not board.is_valid_location(col):
                        score = self.evaluate_powerup(board, powerup, piece, col=col)
                        valid_moves.append(('powerup', powerup, {'col': col, 'score': score}))
                        evaluations += 1
            
            elif powerup == Board.GRAVITY_FLIP:
                score = self.evaluate_powerup(board, powerup, piece)
                valid_moves.append(('powerup', powerup, {'score': score}))
                evaluations += 1
            
            elif powerup == Board.SWAP_COLOR:
                # Try swapping colors in each row and column
                for i in range(Board.ROW_COUNT):
                    if evaluations >= max_evaluations:
                        break
                    score = self.evaluate_powerup(board, powerup, piece, is_row=True, index=i)
                    valid_moves.append(('powerup', powerup, {'is_row': True, 'index': i, 'score': score}))
                    evaluations += 1
                
                for i in range(Board.COLUMN_COUNT):
                    if evaluations >= max_evaluations:
                        break
                    score = self.evaluate_powerup(board, powerup, piece, is_row=False, index=i)
                    valid_moves.append(('powerup', powerup, {'is_row': False, 'index': i, 'score': score}))
                    evaluations += 1
            
            elif powerup == Board.DOUBLE_MOVE:
                # Try enabling double move for each valid column
                for col in range(Board.COLUMN_COUNT):
                    if evaluations >= max_evaluations:
                        break
                    if board.is_valid_location(col):
                        score = self.evaluate_powerup(board, powerup, piece, col=col)
                        valid_moves.append(('powerup', powerup, {'col': col, 'score': score}))
                        evaluations += 1
        
        return valid_moves

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_locations = board.get_valid_locations()
        is_terminal = board.winning_move(board.PLAYER1_PIECE) or board.winning_move(board.PLAYER2_PIECE) or len(valid_locations) == 0
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if board.winning_move(board.PLAYER1_PIECE):
                    return (None, 100000000000000)
                elif board.winning_move(board.PLAYER2_PIECE):
                    return (None, -100000000000000)
                else:  # Game is over, no more valid moves
                    return (None, 0)
            else:  # Depth is zero
                return (None, self.score_position(board, board.PLAYER1_PIECE))

        if maximizingPlayer:
            value = float('-inf')
            column = valid_locations[0]
            
            # First check regular moves
            for col in valid_locations:
                board_copy = board.copy_board()
                board_copy.drop_piece(col, board.PLAYER1_PIECE)
                new_score = self.minimax(board_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            
            # Then check powerup moves if depth > 1
            if depth > 1:
                powerup_moves = self.get_valid_powerup_moves(board, board.PLAYER1_PIECE)
                for move_type, powerup, params in powerup_moves:
                    if params['score'] > value:
                        value = params['score']
                        column = ('powerup', powerup, params)
            
            return column, value

        else:  # Minimizing player
            value = float('inf')
            column = valid_locations[0]
            
            # First check regular moves
            for col in valid_locations:
                board_copy = board.copy_board()
                board_copy.drop_piece(col, board.PLAYER2_PIECE)
                new_score = self.minimax(board_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            
            # Then check powerup moves if depth > 1
            if depth > 1:
                powerup_moves = self.get_valid_powerup_moves(board, board.PLAYER2_PIECE)
                for move_type, powerup, params in powerup_moves:
                    if params['score'] < value:
                        value = params['score']
                        column = ('powerup', powerup, params)
            
            return column, value

    def get_move(self, board):
        """Get the best move considering both regular moves and powerups"""
        column, _ = self.minimax(board, self.depth, float('-inf'), float('inf'), True)
        return column 