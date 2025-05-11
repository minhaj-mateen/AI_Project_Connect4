import random
import math
import time
from board.board import Board

class MonteCarloCustom:
    def __init__(self, piece):
        self.name = "Monte Carlo Tree Search Bot (Custom)"
        self.piece = piece
        self.C = 1.41  # Exploration parameter
        self.time_limit = 0.5  # Reduced time limit to prevent getting stuck
        self.powerup_weights = {
            Board.REMOVE_PIECE: 5,
            Board.GRAVITY_FLIP: 6,
            Board.SWAP_COLOR: 4,
            Board.DOUBLE_MOVE: 8
        }

    def get_move(self, board):
        """Get the best move using Monte Carlo Tree Search with powerups"""
        start_time = time.time()
        root = Node(board, None, None)
        
        # Get available moves including powerups
        available_moves = self.get_available_moves(board)
        
        # If only one move is available, return it immediately
        if len(available_moves) == 1:
            return available_moves[0]
        
        # Run MCTS until time limit
        iterations = 0
        max_iterations = 100  # Safety limit
        while time.time() - start_time < self.time_limit and iterations < max_iterations:
            node = self.select(root)
            if not self.is_terminal(node.board):
                node = self.expand(node)
            reward = self.simulate(node)
            self.backpropagate(node, reward)
            iterations += 1
        
        # Select the best move
        best_move = self.get_best_move(root)
        if best_move is None and available_moves:
            # Fallback to random move if no best move found
            return random.choice(available_moves)
        return best_move

    def is_terminal(self, board):
        """Check if the board is in a terminal state"""
        return (board.winning_move(board.CURR_PLAYER) or
                board.winning_move(3 - board.CURR_PLAYER) or
                len(board.get_valid_locations()) == 0)

    def get_available_moves(self, board):
        """Get all available moves including powerups"""
        moves = []
        valid_locations = board.get_valid_locations()
        
        # Add regular moves
        for col in valid_locations:
            moves.append(col)
        
        # Add powerup moves
        available_powerups = board.get_available_powerups(board.CURR_PLAYER)
        for powerup in available_powerups:
            if powerup == Board.GRAVITY_FLIP:
                moves.append(('powerup', powerup, {}))
            elif powerup == Board.SWAP_COLOR:
                # Add row swaps
                for row in range(Board.ROW_COUNT):
                    moves.append(('powerup', powerup, {'is_row': True, 'index': row}))
                # Add column swaps
                for col in range(Board.COLUMN_COUNT):
                    moves.append(('powerup', powerup, {'is_row': False, 'index': col}))
            elif powerup == Board.REMOVE_PIECE:
                # Add remove piece moves for columns that have pieces
                for col in range(Board.COLUMN_COUNT):
                    if not board.is_valid_location(col):
                        moves.append(('powerup', powerup, {'col': col}))
            elif powerup == Board.DOUBLE_MOVE:
                # Add double move for columns that can fit two pieces
                for col in valid_locations:
                    if board.get_next_open_row(col) > 0:  # Can fit at least one more piece
                        moves.append(('powerup', powerup, {'col': col}))
        
        return moves

    def select(self, node):
        """Select a node to expand using UCB1"""
        while self.is_terminal(node.board):
            if not node.children:
                return node
            node = self.get_best_child(node)
        return node

    def expand(self, node):
        """Expand the node by adding a child"""
        available_moves = self.get_available_moves(node.board)
        if not available_moves:
            return node
        
        # Try moves that haven't been tried yet
        untried_moves = []
        for move in available_moves:
            move_key = self._get_move_key(move)
            if move_key not in node.children:
                untried_moves.append(move)
        
        if untried_moves:
            move = random.choice(untried_moves)
            # Create a new board with the same state
            new_board = node.board.copy_board()
            
            # Apply the move
            if isinstance(move, tuple) and move[0] == 'powerup':
                powerup_type, params = move[1], move[2]
                if powerup_type == Board.GRAVITY_FLIP:
                    new_board.gravity_flip(new_board.CURR_PLAYER)
                elif powerup_type == Board.SWAP_COLOR:
                    new_board.swap_color(new_board.CURR_PLAYER, params['is_row'], params['index'])
                elif powerup_type == Board.REMOVE_PIECE:
                    new_board.remove_piece(params['col'], new_board.CURR_PLAYER)
                elif powerup_type == Board.DOUBLE_MOVE:
                    new_board.enable_double_move(new_board.CURR_PLAYER, params['col'])
            else:
                new_board.drop_piece(move, new_board.CURR_PLAYER)
            
            move_key = self._get_move_key(move)
            child = Node(new_board, node, move)
            node.children[move_key] = child
            return child
        
        return node

    def _get_move_key(self, move):
        """Convert a move to a hashable key for dictionary lookup"""
        if isinstance(move, tuple) and move[0] == 'powerup':
            powerup_type, params = move[1], move[2]
            if powerup_type == Board.GRAVITY_FLIP:
                return ('powerup', powerup_type, 'gravity_flip')
            elif powerup_type == Board.SWAP_COLOR:
                return ('powerup', powerup_type, params['is_row'], params['index'])
            elif powerup_type == Board.REMOVE_PIECE:
                return ('powerup', powerup_type, params['col'])
            elif powerup_type == Board.DOUBLE_MOVE:
                return ('powerup', powerup_type, params['col'])
        return move

    def simulate(self, node):
        """Simulate a random game from the node"""
        # Create a new board with the same state
        board = node.board.copy_board()
        
        depth = 0
        max_depth = 20  # Limit simulation depth
        
        while not self.is_terminal(board) and depth < max_depth:
            available_moves = self.get_available_moves(board)
            if not available_moves:
                break
            move = random.choice(available_moves)
            
            # Apply the move
            if isinstance(move, tuple) and move[0] == 'powerup':
                powerup_type, params = move[1], move[2]
                if powerup_type == Board.GRAVITY_FLIP:
                    board.gravity_flip(board.CURR_PLAYER)
                elif powerup_type == Board.SWAP_COLOR:
                    board.swap_color(board.CURR_PLAYER, params['is_row'], params['index'])
                elif powerup_type == Board.REMOVE_PIECE:
                    board.remove_piece(params['col'], board.CURR_PLAYER)
                elif powerup_type == Board.DOUBLE_MOVE:
                    board.enable_double_move(board.CURR_PLAYER, params['col'])
            else:
                board.drop_piece(move, board.CURR_PLAYER)
            depth += 1
        
        return self.evaluate_terminal(board)

    def backpropagate(self, node, reward):
        """Backpropagate the reward up the tree"""
        while node:
            node.visits += 1
            node.value += reward
            node = node.parent

    def get_best_child(self, node):
        """Get the best child using UCB1"""
        if not node.children:
            return node
        return max(node.children.values(), key=lambda c: self.ucb1(c))

    def get_best_move(self, node):
        """Get the best move from the root node"""
        if not node.children:
            return None
        
        # For powerup moves, consider their weights
        def get_move_score(child):
            if isinstance(child.move, tuple) and child.move[0] == 'powerup':
                return child.visits * self.powerup_weights.get(child.move[1], 1)
            return child.visits
        
        best_child = max(node.children.values(), key=get_move_score)
        return best_child.move

    def ucb1(self, node):
        """Calculate UCB1 value for a node"""
        if node.visits == 0:
            return float('inf')
        exploitation = node.value / node.visits
        exploration = self.C * math.sqrt(math.log(node.parent.visits) / node.visits)
        return exploitation + exploration

    def evaluate_terminal(self, board):
        """Evaluate the terminal state"""
        if board.winning_move(self.piece):
            return 1.0
        elif board.winning_move(3 - self.piece):
            return 0.0
        else:
            return 0.5

class Node:
    def __init__(self, board, parent, move):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = {}
        self.visits = 0
        self.value = 0.0 