############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 1 Starter Code
## v1.0
############################################################

from typing import List
import heapq
from heapq import heappush, heappop
import time
import argparse
import math  # for infinity

from board import *


def is_goal(state):
    """
    Returns True if the state is the goal state and False otherwise.

    :param state: the current state.
    :type state: State
    :return: True or False
    :rtype: bool
    """
    for box in state.board.boxes:
        if box not in state.board.storage:
            return False
    return True


def get_path(state):
    """
    Return a list of states containing the nodes on the path
    from the initial state to the given state in order.

    :param state: The current state.
    :type state: State
    :return: The path.
    :rtype: List[State]
    """
    path = []
    while state != None:
        path.insert(0, state)
        state = state.parent

    return path


def add_tuples(tuple1, tuple2):
    """ adds two tuples as if they're vectors."""
    return tuple([tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]])


def check_valid_move(board, robot, direction):
    """
    Returns true if robot can move in direction on the test_board1.txt, false otherwise.

    test_board1.txt: Board
    robot: Tuple
    direction: Tuple (e.g. (1, 0) or (0, -1))
    """
    new_pos = add_tuples(robot, direction)
    if new_pos in board.obstacles or new_pos in board.robots:
        return False
    elif new_pos in board.boxes:
        new_pos_2 = add_tuples(new_pos, direction)
        if new_pos_2 in board.obstacles or new_pos_2 in board.robots or new_pos_2 in board.boxes:
            return False
    return True


def get_successors(state):
    """
    Return a list containing the successor states of the given state.
    The states in the list may be in any arbitrary order.

    :param state: The current state.
    :type state: State
    :return: The list of successor states.
    :rtype: List[State]
    """

    output = []
    for robot in state.board.robots:
        for direction in {(1, 0), (0, 1), (-1, 0), (0, -1)}:
            if check_valid_move(state.board, robot, direction):
                new_board = Board(state.board.name, state.board.width, state.board.height, [], [], state.board.storage,
                                  state.board.obstacles)

                for rbt in state.board.robots:
                    if rbt != robot:
                        new_board.robots.append(rbt)
                    else:
                        new_board.robots.append(add_tuples(rbt, direction))

                for box in state.board.boxes:
                    if box != (add_tuples(robot, direction)):
                        new_board.boxes.append(box)
                    else:
                        new_board.boxes.append(add_tuples(box, direction))

                new_state = State(new_board, state.hfn, state.hfn(new_board) + state.depth + 1, state.depth + 1, state)
                output.append(new_state)

    return output


def dfs(init_board):
    """
    Run the DFS algorithm given an initial test_board1.txt.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial test_board1.txt.
    :type init_board: Board
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """
    current_state = State(init_board, heuristic_basic, 0, 0, None)
    if is_goal(current_state):
        return get_path(current_state), current_state.depth
    explored = set()
    frontier = get_successors(current_state)
    while len(frontier) != 0:
        if is_goal(current_state):
            return get_path(current_state), current_state.depth

        explored.add(current_state.board)
        current_state = frontier.pop(0)

        for new_state in get_successors(current_state):
            pruning = False
            for explored_board in explored:
                if set(explored_board.robots) == set(new_state.board.robots) and \
                        set(explored_board.boxes) == set(new_state.board.boxes):
                    pruning = True
            if not pruning:
                frontier.append(new_state)
    return [], -1


def a_star(init_board, hfn):
    """
    Run the A_star search algorithm given an initial test_board1.txt and a heuristic function.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial starting test_board1.txt.
    :type init_board: Board
    :param hfn: The heuristic function.
    :type hfn: Heuristic (a function that consumes a Board and produces a numeric heuristic value)
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """

    current_state = State(init_board, hfn, 0, 0, None)
    if is_goal(current_state):
        return get_path(current_state), current_state.depth
    explored = {current_state.board}
    frontier = []
    for new_state in get_successors(current_state):
        heappush(frontier, (new_state.f, new_state))
        explored.add(new_state.board)

    while len(frontier) != 0:
        if is_goal(current_state):
            return get_path(current_state), current_state.f

        current_state = heappop(frontier)[-1]

        for new_state in get_successors(current_state):
            if new_state.board not in explored:
                heappush(frontier, (new_state.f, new_state))
                explored.add(new_state.board)
    return [], -1


def heuristic_basic(board):
    """
    Returns the heuristic value for the given test_board1.txt
    based on the Manhattan Distance Heuristic function.

    Returns the sum of the Manhattan distances between each box
    and its closest storage point.

    :param board: The current test_board1.txt.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    total_distance = 0

    for box in board.boxes:
        shortest = -1
        for storage in board.storage:
            dist = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
            if shortest == -1 or dist < shortest:
                shortest = dist
        total_distance += shortest

    return total_distance


def heuristic_advanced(board):
    """
    An advanced heuristic of your own choosing and invention.

    :param board: The current test_board1.txt.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    total_distance = 0
    closest_bot = -1
    for box in board.boxes:
        if add_tuples(box, (0, 1)) in board.obstacles or add_tuples(box, (0, -1)) in board.obstacles:
            if add_tuples(box, (1, 0)) in board.obstacles or add_tuples(box, (-1, 0)) in board.obstacles:
                if box not in board.storage:
                    return math.inf
        shortest = -1
        for storage in board.storage:
            dist = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
            if shortest == -1 or dist < shortest:
                shortest = dist
        total_distance += shortest
        if shortest != 0:
            for robot in board.robots:
                dist = abs(robot[0] - box[0]) + abs(robot[1] - box[1])
                if closest_bot == -1 or dist < closest_bot:
                    closest_bot = dist

    if total_distance == 0:
        return 0
    return total_distance + closest_bot - 1


def solve_puzzle(board: Board, algorithm: str, hfn):
    """
    Solve the given puzzle using the given type of algorithm.

    :param algorithm: the search algorithm
    :type algorithm: str
    :param hfn: The heuristic function
    :type hfn: Optional[Heuristic]

    :return: the path from the initial state to the goal state
    :rtype: List[State]
    """

    print("Initial test_board1.txt")
    board.display()

    time_start = time.time()

    if algorithm == 'a_star':
        print("Executing A* search")
        path, step = a_star(board, hfn)
    elif algorithm == 'dfs':
        print("Executing DFS")
        path, step = dfs(board, hfn)
    else:
        raise NotImplementedError

    time_end = time.time()
    time_elapsed = time_end - time_start

    if not path:

        print('No solution for this puzzle')
        return []

    else:

        print('Goal state found: ')
        path[-1].board.display()

        print('Solution is: ')

        counter = 0
        while counter < len(path):
            print(counter + 1)
            path[counter].board.display()
            print()
            counter += 1

        print('Solution cost: {}'.format(step))
        print('Time taken: {:.2f}s'.format(time_elapsed))

        return path


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The file that contains the solution to the puzzle."
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=['a_star', 'dfs'],
        help="The searching algorithm."
    )
    parser.add_argument(
        "--heuristic",
        type=str,
        required=False,
        default=None,
        choices=['zero', 'basic', 'advanced'],
        help="The heuristic used for any heuristic search."
    )
    args = parser.parse_args()

    # set the heuristic function
    heuristic = heuristic_zero
    if args.heuristic == 'basic':
        heuristic = heuristic_basic
    elif args.heuristic == 'advanced':
        heuristic = heuristic_advanced

    # read the boards from the file
    board = read_from_file(args.inputfile)

    # solve the puzzles
    path = solve_puzzle(board, args.algorithm, heuristic)

    # save solution in output file
    outputfile = open(args.outputfile, "w")
    counter = 1
    for state in path:
        print(counter, file=outputfile)
        print(state.board, file=outputfile)
        counter += 1
    outputfile.close()
