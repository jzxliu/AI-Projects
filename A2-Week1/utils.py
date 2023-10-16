###############################################################################
# This file contains helper functions and the heuristic functions
# for our AI agents to play the Mancala game.
#
# CSC 384 Fall 2023 Assignment 2
# version 1.0
###############################################################################

import sys
from mancala_game import *

###############################################################################
### DO NOT MODIFY THE CODE BELOW

### Global Constants ###
TOP = 0
BOTTOM = 1

### Errors ###
class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass

### Functions ###
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_opponent(player):
    if player == BOTTOM:
        return TOP
    return BOTTOM

### DO NOT MODIFY THE CODE ABOVE
###############################################################################


def heuristic_basic(board, player):
    """
    Compute the heuristic value of the current test_board1.txt for the current player
    based on the basic heuristic function.

    :param board: the current test_board1.txt.
    :param player: the current player.
    :return: an estimated utility of the current test_board1.txt for the current player.
    """
    top_score = board.mancalas[TOP]
    bottom_score = board.mancalas[BOTTOM]
    if player == BOTTOM:
        return bottom_score - top_score
    return top_score - bottom_score


def heuristic_advanced(board, player): 
    """
    Compute the heuristic value of the current test_board1.txt for the current player
    based on the advanced heuristic function.

    :param board: the current test_board1.txt object.
    :param player: the current player.
    :return: an estimated heuristic value of the current test_board1.txt for the current player.
    """
    top_score = board.mancalas[TOP]
    bottom_score = board.mancalas[BOTTOM]
    top_stones = board.pockets[TOP]
    bottom_stones = board.pockets[BOTTOM]
    if player == BOTTOM:
        return bottom_score - top_score + sum(bottom_stones) - sum(top_stones)
    return top_score - bottom_score + sum(top_stones) - sum(bottom_stones)
