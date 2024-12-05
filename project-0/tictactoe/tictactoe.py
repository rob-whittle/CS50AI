"""
Tic Tac Toe Player
"""

import math, copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]
def player(board):
    """
    Returns player who has the next turn on a board.
    """
    flat_list = [ cell for row in board for cell in row if cell != EMPTY ]

    # X goes first so return X for empty board
    if flat_list == []:
        return X

    # if there are an even number of non-empty cells then X goes, else O goes
    if len(flat_list) % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    # Iterate through board an store index of EMPTY in a set
    return { (i,j) for i, row in enumerate(board) for j, cell in enumerate(row) if cell == EMPTY }

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # check action is valid
    if action not in actions(board):
        raise Exception

    # We don't want to modify the input board so make a deep copy
    new_board = copy.deepcopy(board)

    # Insert the move at the index provided in action
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # check for winning rows by testing if all items in list equal the first item
    for row in board:
        if row[0] != EMPTY and all(cell == row[0] for cell in row):
            return row[0]
    
    # check for winning columns.  First combine the list items using zip
    columns = zip(*board)

    for column in columns:
        if column[0] != EMPTY and all(cell == column[0] for cell in column):
            return column[0]
   
    # check centre value first, if empty no winner as already checked rows and columns
    centre = board[1][1]
    if centre == EMPTY:
        return None
    
    if board[0][0] == centre and board[2][2] == centre:
        return centre

    if board[2][0] == centre and board[0][2] == centre:
        return centre


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # check if game is won
    if winner(board) != None:
        return True

    # check if board full - if no more actions possible
    if len(actions(board)) == 0:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    # player X is trying to maximise
    if player(board) == X:
        # track current best outcome as we step through possible actions
        best_outcome = -99     
        # we step through each of the possible actions for this board state
        # for each action we calculate a new board state - result(board, action)
        # the new board state is passed to the min_value function, which recurses though all the possible permutations to find the best possible result for the action
        # we keep track of the outcome for each action and return the action that resulted in the best outcome for this player
        for action in actions(board):
            outcome = min_value(result(board, action)) # find opponents best moves for each of our possible actions
            if outcome == 1: # this is the best possible outcome for this player so return immediately
                return action
            if outcome > best_outcome:
                best_outcome = outcome
                optimal_action = action
        return optimal_action
    
    # player O is trying to minimise
    if player(board) == O:
        # track current best outcome as we step through possible actions
        best_outcome = 99
        for action in actions(board):
            outcome = max_value(result(board, action)) # find opponents best moves for each of our possible actions
            if outcome == -1: # this is the best possible outcome for this player so return immediately
                return action
            if outcome < best_outcome:
                best_outcome = outcome
                optimal_action = action
        return optimal_action
            
# max_value and min_value functions call each other until a terminal state is found and value returned
def max_value(board):
    """
    Returns the optimal game outcome from the provided board state and action
    """

    # if game is over, return the result
    if terminal(board):
        return utility(board)

    # initialise the value to something smaller than -1
    value = -99

    # calculate new board state for each action and pass to min_value to figure out opponents optimal move
    for action in actions(board):
        value = max(value, min_value(result(board, action)))
        if value == 1: # this is the best possible outcome so return immediately
            return value
    
    # once all possible actions exhausted return the final max value
    return value

def min_value(board):
    """
    Returns the action that results in the lowest board value
    """
    # if game is over, return the result
    if terminal(board):
        return utility(board)

    # initialise the value to something larger than 1
    value = 99

    # calculate new board state for each action and pass to max_value to figure out opponents optimal move
    for action in actions(board):
        value = min(value, max_value(result(board, action)))
        if value == -1: # this is the best possible outcome so return immediately
            return value    
    
    # once all possible actions exhausted return the final min value
    return value