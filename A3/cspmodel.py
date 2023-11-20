############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.1
## Changes:
##   v1.1: updated the comments in kropki_model. 
##         the second return value should be a 2d list of variables.
############################################################

from board import *
from cspbase import *


def kropki_model(board):
    """
    Create a CSP for a Kropki Sudoku Puzzle given a board of dimension.

    If a variable has an initial value, its domain should only contain the initial value.
    Otherwise, the variable's domain should contain all possible values (1 to dimension).

    We will encode all the constraints as binary constraints.
    Each constraint is represented by a list of tuples, representing the values that
    satisfy this constraint. (This is the table representation taught in lecture.)

    Remember that a Kropki sudoku has the following constraints.
    - Row constraint: every two cells in a row must have different values.
    - Column constraint: every two cells in a column must have different values.
    - Cage constraint: every two cells in a 2x3 cage (for 6x6 puzzle) 
            or 3x3 cage (for 9x9 puzzle) must have different values.
    - Black dot constraints: one value is twice the other value.
    - White dot constraints: the two values are consecutive (differ by 1).

    Make sure that you return a 2D list of variables separately. 
    Once the CSP is solved, we will use this list of variables to populate the solved board.
    Take a look at csprun.py for the expected format of this 2D list.

    :returns: A CSP object and a list of variables.
    :rtype: CSP, List[List[Variable]]

    """
    dim = board.dimension
    vars = create_variables(dim)
    csp = CSP("Kropki", vars)

    diff_tuples = satisfying_tuples_difference_constraints(dim)
    white_tuples = satisfying_tuples_white_dots(dim)
    black_tuples = satisfying_tuples_black_dots(dim)

    diff_constraints = create_row_and_col_constraints(dim, diff_tuples, vars)
    print(len(diff_constraints))
    cage_constraints = create_cage_constraints(dim, diff_tuples, vars)
    print(len(cage_constraints))
    dot_constraints = create_dot_constraints(dim, board.dots, white_tuples, black_tuples, vars)
    print(len(dot_constraints))

    for c in diff_constraints:
        csp.add_constraint(c)

    for c in cage_constraints:
        csp.add_constraint(c)

    for c in dot_constraints:
        csp.add_constraint(c)

    vars_2d = [[0] * dim] * dim
    for row in range(dim):
        for col in range(dim):
            vars_2d[row][col] = vars[row * dim + col]
    return csp, vars_2d


def create_initial_domain(dim):
    """
    Return a list of values for the initial domain of any unassigned variable.
    [1, 2, ..., dimension]

    :param dim: board dimension
    :type dim: int

    :returns: A list of values for the initial domain of any unassigned variable.
    :rtype: List[int]
    """

    return list(range(1, dim + 1))


def create_variables(dim):
    """
    Return a list of variables for the board.

    We recommend that your name each variable Var(row, col).

    :param dim: Size of the board
    :type dim: int

    :returns: A list of variables, one for each cell on the board
    :rtype: List[Variables]
    """

    variables = []
    for row in range(dim):
        for col in range(dim):
            variables.append(Variable("Var(" + str(row) + ", " + str(col) + ").", create_initial_domain(dim)))
    return variables


def satisfying_tuples_difference_constraints(dim):
    """
    Return a list of satisfying tuples for binary difference constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satisfying tuples
    :rtype: List[(int,int)]
    """
    tuples = []
    for i in range(1, dim + 1):
        for j in range(1, dim + 1):
            if i != j:
                tuples.append((i, j))
    return tuples


def satisfying_tuples_white_dots(dim):
    """
    Return a list of satisfying tuples for white dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satisfying tuples
    :rtype: List[(int,int)]
    """
    tuples = []
    for i in range(1, dim + 1):
        for j in range(1, dim + 1):
            if i + 1 == j or i == j + 1:
                tuples.append((i, j))
    return tuples


def satisfying_tuples_black_dots(dim):
    """
    Return a list of satisfying tuples for black dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satisfying tuples
    :rtype: List[(int,int)]
    """
    tuples = []
    for i in range(1, dim + 1):
        for j in range(1, dim + 1):
            if i * 2 == j or i == j * 2:
                tuples.append((i, j))
    return tuples


def create_row_and_col_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different row/column constraints.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    constraints = []
    for i in range(dim):
        for j in range(dim):
            for k in range(j + 1, dim):
                # Row Constraint
                x = Constraint("Row " + str((i, j)) + ", " + str((i, k)), [variables[i * dim + j], variables[i * dim + k]])
                x.add_satisfying_tuples(sat_tuples)
                constraints.append(x)

                # Column Constraint
                y = Constraint("Col " + str((j, i)) + ", " + str((k, i)), [variables[j * dim + i], variables[k * dim + i]])
                y.add_satisfying_tuples(sat_tuples)
                constraints.append(y)

    return constraints


def create_cage_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different constraints for all cages.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    constraints = []

    if dim == 6:
        for x1 in [0, 2, 4]:
            x2 = x1 + 1
            for y1 in range(dim):
                for y2 in range(dim):
                    if y1 != y2 and (y1 // 3 == y2 // 3):
                        var1 = variables[y1 * dim + x1]
                        var2 = variables[y2 * dim + x2]
                        constraint = Constraint("Cage " + str(var1) + ", " + str(var2), [var1, var2])
                        constraint.add_satisfying_tuples(sat_tuples)
                        constraints.append(constraint)
    if dim == 9:
        for x1 in range(dim):
            for y1 in range(dim):
                for x2 in range(dim):
                    for y2 in range(dim):
                        if (x1 // 3 == x2 // 3) and (y1 // 3 == y2 // 3):
                            var1 = variables[x1 * dim + y1]
                            var2 = variables[x2 * dim + y2]
                            constraint = Constraint("Cage " + str(var1) + ", " + str(var2), [var1, var2])
                            constraint.add_satisfying_tuples(sat_tuples)
                            constraints.append(constraint)
    return constraints


def create_dot_constraints(dim, dots, white_tuples, black_tuples, variables):
    """
    Create and return a list of binary constraints, one for each dot.

    :param dim: Size of the board
    :type dim: int
    
    :param dots: A list of dots, each dot is a Dot object.
    :type dots: List[Dot]

    :param white_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the white dot constraint.
    :type white_tuples: List[(int, int)]
    
    :param black_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the black dot constraint.
    :type black_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary dot constraints
    :rtype: List[Constraint]
    """

    constraints = []
    for dot in dots:
        var1 = variables[dot.cell_row * dim + dot.cell_col]
        var2 = variables[dot.cell2_row * dim + dot.cell2_col]

        constraint = Constraint("Dot " + str(var1) + " and " + str(var2), [var1, var2])
        if dot.color == CHAR_BLACK:
            constraint.add_satisfying_tuples(black_tuples)
        elif dot.color == CHAR_WHITE:
            constraint.add_satisfying_tuples(white_tuples)
        constraints.append(constraint)

    return constraints
