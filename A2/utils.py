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
    self_mancala = board.mancalas[player]
    opponent_mancala = board.mancalas[get_opponent(player)]
    self_pockets = sum(board.pockets[player])
    opponent_pockets = sum(board.pockets[get_opponent(player)])
    if sum(board.pockets[player]) == 0 or sum(board.pockets[get_opponent(player)]) == 0:
        return self_mancala - opponent_mancala + self_pockets - opponent_pockets
    return self_mancala - opponent_mancala


def heuristic_advanced(board, player):
    """
    Compute the heuristic value of the current test_board1.txt for the current player
    based on the advanced heuristic function.

    :param board: the current test_board1.txt object.
    :param player: the current player.
    :return: an estimated heuristic value of the current test_board1.txt for the current player.
    """
    self_mancala = board.mancalas[player]
    opponent_mancala = board.mancalas[get_opponent(player)]
    self_pockets = sum(board.pockets[player])
    opponent_pockets = sum(board.pockets[get_opponent(player)])
    return self_mancala - opponent_mancala + self_pockets - opponent_pockets
