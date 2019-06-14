# === Model ===
# shape of the game's state
import random
import pprint
from itertools import product, filterfalse, chain
from collections import defaultdict, namedtuple
from enum import Enum

pp = pprint.PrettyPrinter(indent=4)

# state: 1) marked 2) revealed 3) hidden
# content: 1) space 2) distance 3) mine; represented as -1, [1, inf], 0

CellState = Enum('CellState', ('MARKED REVEALED HIDDEN'))
CellContent = Enum('CellContent', ('MINE SPACE'))
class Cell:
    def __init__(self, state, content):
        self.state = state
        self.content = content

    def __eq__(self, other):
        return self.state == other.state and self.content == other.content

    def __repr__(self):
        return f'''Cell({self.state}, {self.content})'''

random.seed(42)

def new_cell(content):
    return Cell(CellState.HIDDEN, content)

def adjacent(i, j, height, width):
    adjs = [
        (i+1,j),
        (i+1,j+1),
        (i,j+1),
        (i-1,j+1),
        (i-1,j),
        (i-1,j-1),
        (i, j-1),
        (i+1,j-1)
    ]
    return {
        (k, l) for k, l in adjs if 0 <= k < height and 0 <= l < width
    }

def num_mine_adjacent(i, j, board):
    height = len(board)
    width = len(board[0])
    return sum(
        1
        for k,l in adjacent(i, j, height, width)
        if board[k][l] == Cell(CellState.HIDDEN, CellContent.MINE)
    )

def new_board(height, width, num_mines, pos_be_space):
    if pos_be_space[0] >= height or pos_be_space[1] >= width:
        raise ValueError("Impossible position for space.")
    if num_mines > height * width:
        raise ValueError("Impossible number of mines.")
    board =  [[new_cell(False) for _ in range(width)] for _ in range(height)]
    mine_indices = set(random.sample(
        list(filterfalse(
            lambda coor: pos_be_space == coor, product(range(height), range(width))
        )),
        num_mines
    ))
    for i,j in product(range(height), range(width)):
        if (i, j) in mine_indices:
            board[i][j] = new_cell(CellContent.MINE)
    for i, j in product(range(height), range(width)):
        if board[i][j] != new_cell(CellContent.MINE):
            board[i][j] = new_cell(num_mine_adjacent(i, j, board) or CellContent.SPACE)
    return board

def test_new_cell():
    assert new_cell(CellContent.MINE) == Cell(CellState.HIDDEN, CellContent.MINE)
    assert new_cell(3) == Cell(CellState.HIDDEN, 3)

def test_new_board():
    num_mines = 2
    height = 2
    width = 3
    pos_be_space = (0,2)
    result_board = new_board(height, width, num_mines, pos_be_space)
    assert len(result_board) == height and len(result_board[0]) == width
    assert result_board[pos_be_space[0]][pos_be_space[1]] != Cell(CellState.HIDDEN, CellContent.MINE)
    assert num_mines == sum(
        1 for cell in chain(*result_board) if cell == Cell(CellState.HIDDEN, CellContent.MINE)
    )
    assert result_board == [
        [   Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 2), Cell(CellState.HIDDEN, 1)],
        [   Cell(CellState.HIDDEN, 1),                Cell(CellState.HIDDEN, 2), Cell(CellState.HIDDEN, CellContent.MINE)]
    ]

# board is then a collection of cells

# Public APIs
# 1) change state of a cell, if a space revealed recursively revealed adjacent cells, base cases being cells adjacent to mines
# 2) Get a new board - i.e. initalize cells' contents and state
# 3) is the game over from looking at the board

# === View ===
# 1) Convert board to STDOUT presentatable format

# === Controller ===
# 1) Get input from STDOUT from user for (in this order) a) board size b) first choice c) revealation command d) mark command
# 2) After first move, check if game's ended after each move, show new game state on stdout
