Project Title:
Advanced AI Agents for Classic and Power-Up Variants of Connect 4

Submitted By:
Minhaj Mateen - 22K-4519
Ezaan Hussain - 22K-4531
Taushar Khatri - 22K-4260

Course:
AI

Instructor:
Khalid Khan

Submission Date:
05/11/25

1. Executive Summary

Project Overview:
This project explores strategic AI gameplay in both the classic Connect 4 and a modified version featuring power-ups. The main objective was to develop intelligent agents capable of competitive play using Minimax, Alpha-Beta Pruning, and Monte Carlo Tree Search (MCTS). The power-up variant introduces new mechanics—Remove Disc, Board Flip, Swap Positions, and Double Turn—that significantly affect game strategy. Each AI technique was adapted to handle both the traditional and altered rule sets, with the aim of assessing their effectiveness and robustness under varied conditions.

2. Introduction

Background:
Connect 4 is a two-player strategy game where players alternately drop discs into a vertical grid, aiming to form a line of four of their own discs. The simplicity and deterministic nature of the game make it a great candidate for AI experimentation. To further increase complexity and depth, we designed a variant with power-ups that disrupt the usual flow of gameplay, making it a more dynamic and challenging environment for AI decision-making.

Objectives of the Project:
Develop AI agents using Minimax, Alpha-Beta Pruning, and MCTS.
Integrate AI with both classic and power-up enhanced Connect 4.
Analyze performance across agents and game versions.
Evaluate robustness and adaptability of AI under modified rules.

3. Game Description

Original Game Rules:
In classic Connect 4:
Players take turns dropping discs into a 7x6 grid.
Discs occupy the lowest available position in the column.
The first player to align four of their discs vertically, horizontally, or diagonally wins.
The game ends in a draw if the grid is completely filled with no winner.

Innovations and Modifications:
We added a power-up system where each player can use each power-up once per game:
Remove Disc: Remove one of your own discs from the board.
Board Flip: Vertically flip the entire board state.
Swap Positions: Swaps color of discs on any row or column the board.
Double Turn: Take two consecutive turns.
These mechanics introduce non-linearity and increase the search complexity for AI agents.

4. AI Approach and Methodology

AI Techniques Used:
Minimax: Used to simulate future states and select the optimal move under the assumption that the opponent plays optimally.
Alpha-Beta Pruning: Optimization of Minimax to reduce unnecessary computations.
Monte Carlo Tree Search (MCTS): Probabilistic approach that performs simulations to statistically estimate the best moves, especially effective in the modified game due to increased branching factor.

Algorithm and Heuristic Design:
The evaluation function for Minimax/Alpha-Beta considers:
Number of 2-in-a-row, 3-in-a-row sequences.
Center column preference.
Blocking opponent's threats.
Adjustments for power-up availability and use.
MCTS simulations run thousands of playouts per move and adapt naturally to the probabilistic nature of power-ups.

AI Performance Evaluation:
Metrics: Win rate, decision-making time, and adaptability.
Each agent was tested in 100 matches (classic + power-up mode) against human and AI opponents.
Performance was logged and compared statistically.

5. Game Mechanics and Rules

Modified Game Rules:
Each player can use each power-up once per game.
Power-ups must be used at the start of a player’s turn.
Power-ups cannot be used consecutively.
The grid size remains 7x6.

Turn-based Mechanics:
Players alternate turns.
After a power-up is used (if any), the player plays their regular move.
Game ends on win or draw condition as in the original game.

Winning Conditions:
Same as classic Connect 4: four discs in a line (vertical, horizontal, diagonal).
Power-ups can help or disrupt formation of winning sequences but don’t change the win condition.

6. Implementation and Development

Development Process:
The game and AI were developed iteratively using object-oriented principles.
Custom game engine handled both classic and power-up modes.
Separate modules were created for each AI agent for comparison and testing.
Programming Languages and Tools:
Programming Language: Python
Libraries: NumPy, random, copy

Tools: GitHub (version control), VSCode (IDE)

Challenges Encountered:
Balancing power-up impact: Some power-ups were initially too disruptive.
MCTS tuning: Number of playouts vs. response time required careful optimization.
Handling increased branching factor due to power-ups in Minimax was computationally expensive and required pruning strategies.

7. Team Contributions

Team Members and Responsibilities:
Ezaan Hussain: Developed and optimized Minimax and Alpha-Beta pruning agents.
Minhaj Mateen: Implemented power-up logic and integrated it with game rules.
Taushar: Developed MCTS agent and fine-tuned simulation parameters.

8. Results and Discussion

AI Performance:
MCTS excelled in power-up mode thanks to its ability to handle non-determinism and dynamic state changes.
Minimax performed best in both classic and custom
Minimax was consistent but slower and less adaptive in the modified variant.

9. References

Wikipedia: Connect Four
GeeksforGeeks: Minimax and Alpha-Beta Pruning tutorials.
Pygame Documentation (https://www.pygame.org/docs/)
ChatGpt
Github