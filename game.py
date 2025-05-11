import sys
import os
import pygame
import numpy as np
import math
import random
import time
from bots import *
from board import *
from players.human import Human
from players.human_custom import HumanCustom
from bots.minimax_custom import MinimaxCustom

# Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

class Connect4Game:
    def __init__(self, p1, p2, ui=True):
        self.p1 = p1
        self.p2 = p2
        self.ui = ui
        self.board = Board(random.randint(Board.PLAYER1_PIECE, Board.PLAYER2_PIECE))
        self.graphics_board = GBoard(self.board) if ui else None
        self.game_over = False
        self.turn = self.board.CURR_PLAYER
        self.time_p1 = self.time_p2 = 0
        self.moves_count_p1 = self.moves_count_p2 = 0
        self.PLAYER_COLOUR = [GBoard.RED, GBoard.YELLOW]
        self.human_move = None
        self.waiting_for_human = False

    def next_turn(self):
        print(f"\nPlayer {self.turn}'s Turn\n")
        self.board.print_board()
        if self.ui:
            self.graphics_board.draw_gboard(self.board)
            self.graphics_board.update_gboard()

        self.turn = Board.PLAYER2_PIECE if self.turn == Board.PLAYER1_PIECE else Board.PLAYER1_PIECE

    def check_win(self, piece):
        if self.board.winning_move(piece):
            if self.ui:
                self.graphics_board.write_on_board(f"PLAYER {piece} WINS!", 
                                                 self.PLAYER_COLOUR[piece - 1], 350, 50, 70, True)
                self.graphics_board.update_gboard()
            print(f"\nPLAYER {piece} WINS!")
            return True
        
        if self.board.check_draw():
            if self.ui:
                self.graphics_board.write_on_board("IT'S A TIE!", self.graphics_board.LIGHTBLUE, 350, 50, 70, True)
                self.graphics_board.update_gboard()
            print("\nIT'S A TIE!")
            return True
        return False

    def handle_move(self, move, player_piece):
        if isinstance(move, tuple):
            if move[0] == 'powerup':
                powerup_type = move[1]
                params = move[2]
                success = self.board.use_powerup(powerup_type, player_piece, **params)
                if success:
                    print(f"Player {player_piece} used powerup {powerup_type}")
                    if self.ui:
                        self.graphics_board.draw_gboard(self.board)
                        self.graphics_board.update_gboard()
                    return True
                return False
            elif move[0] == 'double':
                col = move[1]
                if self.board.is_valid_location(col):
                    # Execute first move
                    self.board.drop_piece(col, player_piece)
                    # Set up for second move
                    self.board.double_move_available[player_piece] = True
                    self.board.double_move_column[player_piece] = col
                    if self.ui:
                        self.graphics_board.draw_gboard(self.board)
                        self.graphics_board.update_gboard()
                    return True
                return False
        else:
            if self.board.is_valid_location(move):
                # If this is a second move of a double move, check the column
                if self.board.double_move_available[player_piece]:
                    if move != self.board.double_move_column[player_piece]:
                        print("Invalid move: Must use the same column for double move")
                        return False
                self.board.drop_piece(move, player_piece)
                # Reset double move state after second move
                if self.board.double_move_available[player_piece]:
                    self.board.double_move_available[player_piece] = False
                    self.board.double_move_column[player_piece] = None
                if self.ui:
                    self.graphics_board.draw_gboard(self.board)
                    self.graphics_board.update_gboard()
                return True
        return False

    def handle_human_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            posx = event.pos[0]
            col = int(math.floor(posx / self.graphics_board.SQUARESIZE))
            if self.board.is_valid_location(col):
                self.human_move = col
                self.waiting_for_human = False
                return True
        return False

    def play(self):
        self.board.print_board()
        if self.ui:
            self.graphics_board.draw_gboard(self.board)
            self.graphics_board.update_gboard()

        while not self.game_over:
            # Handle events for human players
            if self.ui:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if isinstance(self.p1, Human) and self.turn == Board.PLAYER1_PIECE:
                        self.handle_human_input(event)
                    elif isinstance(self.p2, Human) and self.turn == Board.PLAYER2_PIECE:
                        self.handle_human_input(event)

            # Player 1's turn
            start = time.perf_counter()
            if self.turn == Board.PLAYER1_PIECE and not self.game_over:
                if isinstance(self.p1, Human):
                    if self.human_move is not None:
                        move = self.human_move
                        self.human_move = None
                    else:
                        continue
                else:
                    move = self.p1.get_move(self.board)
                
                if self.handle_move(move, Board.PLAYER1_PIECE):
                    self.moves_count_p1 += 1
                    # Only switch turns if not in double move state
                    if not self.board.double_move_available[Board.PLAYER1_PIECE]:
                        self.next_turn()
                    self.game_over = self.check_win(Board.PLAYER1_PIECE)
            end = time.perf_counter()
            self.time_p1 += (end - start)

            # Player 2's turn
            start = time.perf_counter()
            if self.turn == Board.PLAYER2_PIECE and not self.game_over:
                if isinstance(self.p2, Human):
                    if self.human_move is not None:
                        move = self.human_move
                        self.human_move = None
                    else:
                        continue
                else:
                    move = self.p2.get_move(self.board)
                
                if self.handle_move(move, Board.PLAYER2_PIECE):
                    self.moves_count_p2 += 1
                    # Only switch turns if not in double move state
                    if not self.board.double_move_available[Board.PLAYER2_PIECE]:
                        self.next_turn()
                    self.game_over = self.check_win(Board.PLAYER2_PIECE)
            end = time.perf_counter()
            self.time_p2 += (end - start)

            if self.game_over:
                if self.ui:
                    pygame.time.wait(1000)
                self.print_game_stats()
                if self.ui:
                    sys.exit()

    def print_game_stats(self):
        print("\nPlayer 1")
        print(f"TIME: {round(self.time_p1, 2):.2f} seconds")
        print(f"MOVES: {self.moves_count_p1}")
        print("\nPlayer 2")
        print(f"TIME: {round(self.time_p2, 2):.2f} seconds")
        print(f"MOVES: {self.moves_count_p2}")

# Bot configuration
BOT_CONFIG = {
    'human': {'class': Human, 'name': 'Human'},
    'minimax': {'class': MiniMaxBot, 'name': 'MiniMax Bot'},
    'montecarlo': {'class': MonteCarloBot, 'name': 'Monte Carlo Tree Search Bot'},
    'human_custom': {'class': HumanCustom, 'name': 'Human (Custom)'},
    'minimax_custom': {'class': MinimaxCustom, 'name': 'MiniMax Bot (Custom)'},
    'montecarlo_custom': {'class': MonteCarloCustom, 'name': 'Monte Carlo Tree Search Bot (Custom)'}
}

def create_player(player_type, piece):
    if player_type is None or player_type == "human":
        return Human(piece)
    
    if player_type in BOT_CONFIG:
        return BOT_CONFIG[player_type]['class'](piece)
    
    print(f"Error: Unknown player type '{player_type}'")
    sys.exit(1)

def start_game(p1_type, p2_type, ui=True):
    p1 = create_player(p1_type, Board.PLAYER1_PIECE)
    p2 = create_player(p2_type, Board.PLAYER2_PIECE)

    print(f"\nPlayer 1 is set as a {BOT_CONFIG.get(p1_type, {'name': 'Human'})['name']}")
    print(f"Player 2 is set as a {BOT_CONFIG.get(p2_type, {'name': 'Human'})['name']}\n")

    if not ui and (isinstance(p1, Human) or isinstance(p2, Human)):
        print("Error: Cannot play game as Human without UI!")
        sys.exit(1)

    game = Connect4Game(p1, p2, ui)
    game.play()

def main():
    main_screen()

def main_screen():
    pygame.init()
    pygame.display.set_caption("Connect Four | AI Project")
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    def human_vs_human():
        start_game("human", "human")

    def custom_game():
        custom_game_screen()

    player_vs_player_button = graphics_board.create_button(60, 220, 300, 40, '1. PLAYER VS PLAYER', human_vs_human)
    player_vs_bot_button = graphics_board.create_button(60, 280, 300, 40, '2. PLAYER VS BOT', bot_vs_human_screen)
    bot_vs_bot_button = graphics_board.create_button(60, 340, 300, 40, '3. BOT VS BOT', bot_vs_bot_screen)
    custom_game_button = graphics_board.create_button(60, 400, 300, 40, '4. CUSTOM GAME', custom_game)
    quit_button = graphics_board.create_button(60, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [player_vs_player_button, player_vs_bot_button, bot_vs_bot_button, custom_game_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE ONE OF THE OPTIONS TO PLAY", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def bot_vs_human_screen():
    pygame.init()
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    def human_vs_minimax():
        start_game("human", "minimax")
    
    def human_vs_montecarlo():
        start_game("human", "montecarlo")

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT', human_vs_minimax)
    montecarlo_button = graphics_board.create_button(60, 280, 400, 40, '2. MONTECARLO SEARCH BOT', human_vs_montecarlo)
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', main_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, montecarlo_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE THE BOT TO PLAY AGAINST", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def bot_vs_bot_screen():
    pygame.init()
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    first_bot = second_bot = None

    def bots_to_play_against(bot_to_play):
        nonlocal first_bot, second_bot

        if first_bot == None:
            first_bot = bot_to_play
        elif second_bot == None and first_bot != None:
            second_bot= bot_to_play

        if first_bot != None and second_bot != None:
            start_game(first_bot, second_bot, ui=True)  # Disable UI for bot vs bot

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT',  bots_to_play_against, ("minimax"))
    montecarlo_button = graphics_board.create_button(60, 280, 400, 40, '2. MONTECARLO SEARCH BOT', bots_to_play_against, ("montecarlo"))
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', main_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, montecarlo_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE ANY TWO BOT(S) TO PLAY", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            if(button['args'] != None):
                                button['callback'](button['args'])
                            else:
                                button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE                
        
        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def custom_game_screen():
    pygame.init()
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    def custom_human_vs_human():
        start_game("human_custom", "human_custom")

    def custom_human_vs_bot():
        custom_human_vs_bot_screen()

    def custom_bot_vs_bot():
        custom_bot_vs_bot_screen()

    player_vs_player_button = graphics_board.create_button(60, 220, 300, 40, '1. PLAYER VS PLAYER', custom_human_vs_human)
    player_vs_bot_button = graphics_board.create_button(60, 280, 300, 40, '2. PLAYER VS BOT', custom_human_vs_bot)
    bot_vs_bot_button = graphics_board.create_button(60, 340, 300, 40, '3. BOT VS BOT', custom_bot_vs_bot)
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', main_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [player_vs_player_button, player_vs_bot_button, bot_vs_bot_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE ONE OF THE OPTIONS TO PLAY", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def custom_human_vs_bot_screen():
    pygame.init()
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    def human_vs_minimax():
        start_game("human_custom", "minimax")

    def human_vs_minimax_custom():
        start_game("human_custom", "minimax_custom")

    def human_vs_montecarlo_custom():
        start_game("human_custom", "montecarlo_custom")

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT', human_vs_minimax)
    minimax_custom_button = graphics_board.create_button(60, 280, 400, 40, '2. MINIMAX BOT (CUSTOM)', human_vs_minimax_custom)
    montecarlo_custom_button = graphics_board.create_button(60, 340, 400, 40, '3. MONTECARLO BOT (CUSTOM)', human_vs_montecarlo_custom)
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', custom_game_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, minimax_custom_button, montecarlo_custom_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CUSTOM GAME MODE", graphics_board.RED, 350, 100, 60, True)
        graphics_board.write_on_board("CHOOSE THE BOT TO PLAY AGAINST", graphics_board.YELLOW, 350, 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def custom_bot_vs_bot_screen():
    pygame.init()
    temp_board = Board(1)
    graphics_board = GBoard(temp_board)

    first_bot = second_bot = None

    def bots_to_play_against(bot_to_play):
        nonlocal first_bot, second_bot

        if first_bot == None:
            first_bot = bot_to_play
        elif second_bot == None and first_bot != None:
            second_bot = bot_to_play

        if first_bot != None and second_bot != None:
            start_game(first_bot, second_bot, ui=False)  # Disable UI for bot vs bot

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT', bots_to_play_against, ("minimax"))
    minimax_custom_button = graphics_board.create_button(60, 280, 400, 40, '2. MINIMAX BOT (CUSTOM)', bots_to_play_against, ("minimax_custom"))
    montecarlo_custom_button = graphics_board.create_button(60, 340, 400, 40, '3. MONTECARLO BOT (CUSTOM)', bots_to_play_against, ("montecarlo_custom"))
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', custom_game_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, minimax_custom_button, montecarlo_custom_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CUSTOM GAME MODE", graphics_board.RED, 350, 100, 60, True)
        graphics_board.write_on_board("CHOOSE ANY TWO BOT(S) TO PLAY", graphics_board.YELLOW, 350, 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            if(button['args'] != None):
                                button['callback'](button['args'])
                            else:
                                button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

if __name__ == '__main__':
    main()
