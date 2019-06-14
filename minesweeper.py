# === Model ===
# shape of the game's state
import random
import pprint
import copy
from functools import reduce, partial
from itertools import product, filterfalse, chain
from enum import Enum

pp = pprint.PrettyPrinter(indent=4)
random.seed(42)

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


def new_board(height, width, num_mines, pos_be_revealed):
    if pos_be_revealed[0] >= height or pos_be_revealed[1] >= width:
        raise ValueError("Impossible position for space.")
    if num_mines > height * width:
        raise ValueError("Impossible number of mines.")
    board =  [[new_cell(False) for _ in range(width)] for _ in range(height)]
    mine_indices = set(random.sample(
        list(filterfalse(
            lambda coor: pos_be_revealed == coor, product(range(height), range(width))
        )),
        num_mines
    ))
    for i,j in product(range(height), range(width)):
        if (i, j) in mine_indices:
            board[i][j] = new_cell(CellContent.MINE)
    for i, j in product(range(height), range(width)):
        if board[i][j] != new_cell(CellContent.MINE):
            board[i][j] = new_cell(num_mine_adjacent(i, j, board) or CellContent.SPACE)

    board_revealed_pos_be_revealed = board_revealed_at_cell(pos_be_revealed, board)

    return board_revealed_pos_be_revealed


def board_revealed_at_cell(cell_number, board):
    ''' Reveal the cell at cell_number, if it's a space recursively reveval adjacent
    cells, if it's a number, reveal just that
    '''
    i = cell_number[0]
    j = cell_number[1]
    if board[i][j].state == CellState.REVEALED:
        return board
    height = len(board)
    width = len(board[0])

    result_board = copy.deepcopy(board)
    result_board[i][j].state = CellState.REVEALED

    if result_board[i][j].content != CellContent.SPACE:
        return result_board

    for k,l in adjacent(i, j, height, width):
        result_board = board_revealed_at_cell((k,l), result_board)

    return result_board

def is_game_won(board):
    return all((cell.state == CellState.REVEALED and cell.content != CellContent.MINE) or (cell.state == CellState.HIDDEN and cell.content == CellContent.MINE)
               for cell in chain(*board))


def is_game_over(board):
    return any(cell.state == CellState.REVEALED and cell.content == CellContent.MINE for cell in chain(*board))


# === Model Tests ===
def test_new_cell():
    assert new_cell(CellContent.MINE) == Cell(CellState.HIDDEN, CellContent.MINE)
    assert new_cell(3) == Cell(CellState.HIDDEN, 3)


def test_new_board():
    num_mines = 5
    height = 5
    width = 5
    pos_be_revealed = (0,2)
    result_board = new_board(height, width, num_mines, pos_be_revealed)
    # correct size
    assert len(result_board) == height and len(result_board[0]) == width
    # first location is revealed
    assert result_board[pos_be_revealed[0]][pos_be_revealed[1]].state == CellState.REVEALED
    assert result_board[pos_be_revealed[0]][pos_be_revealed[1]].content != CellContent.MINE
    # correct number of mines
    assert num_mines == sum(
        1 for cell in chain(*result_board) if cell == Cell(CellState.HIDDEN, CellContent.MINE)
    )




def test_board_revaled_at_cell():
    test_board = [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)]
    ]
    result_board = board_revealed_at_cell((2, 0), test_board)
    assert result_board == [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1)],
        [Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)]
    ]

    test_board2 = [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, 2), Cell(CellState.HIDDEN, CellContent.MINE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, 2), Cell(CellState.HIDDEN, CellContent.MINE)],
        [Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE)]
    ]
    expected_board2 = [
        [Cell(CellState.HIDDEN, CellContent.MINE),    Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, 2), Cell(CellState.HIDDEN, CellContent.MINE)],
        [Cell(CellState.REVEALED, 1),                 Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, 2), Cell(CellState.HIDDEN, CellContent.MINE)],
        [Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE)]
    ]
    result_board2 = board_revealed_at_cell((0,2), test_board2)
    assert result_board2 == expected_board2


def test_is_game_over():
    not_finished_board = [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)]
    ]
    assert not is_game_over(not_finished_board)

    not_finished_board1 = [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)]
    ]
    assert not is_game_over(not_finished_board1)

    finished_board2 = [
        [Cell(CellState.REVEALED, CellContent.MINE), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1), Cell(CellState.HIDDEN, 1)],
        [Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.HIDDEN, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.MINE), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)]
    ]
    assert is_game_over(finished_board2)


def test_is_game_won():
    finished_board = [
        [Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.REVEALED, 1)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1)],
        [Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)],
        [Cell(CellState.REVEALED, 1), Cell(CellState.HIDDEN, CellContent.MINE), Cell(CellState.REVEALED, 1), Cell(CellState.REVEALED, CellContent.SPACE), Cell(CellState.REVEALED, CellContent.SPACE)]
    ]
    assert is_game_won(finished_board)


# === View Functions ===

def cell_view(cell, revealed=False):
    if cell.state == CellState.HIDDEN and not revealed:
        return 'X'
    if cell.content == CellContent.SPACE:
        return '-'
    if cell.content == CellContent.MINE:
        return 'M'
    return str(cell.content)



def board_view(board, revealed=False):
    rows = [', '.join([cell_view(cell, revealed) for cell in row]) for idx, row in enumerate(board)]
    rows_indexed = [f'{idx}    ' + row_strrep for idx,row_strrep in enumerate(rows)]
    rows_newlined = '\n'.join(rows_indexed)
    return '     ' + '  '.join([str(col_num)for col_num in range(len(board[0]))]) + '\n\n' + rows_newlined


def ask_cell_num():
    return tuple(int(v.strip()) for v in tuple(
        input('''cell number (e.g. 0,2)? ''').split(',')
    ))


if __name__ == '__main__':
    height = int(input('''height (e.g. 5)? '''))
    width = int(input('''width (e.g. 5)? '''))
    num_mines = int(input('''number of mines (e.g. 4)? '''))
    first_cell_num = ask_cell_num()
    board = new_board(height, width, num_mines, first_cell_num)
    game_is_won = is_game_won(board)
    game_is_over = is_game_over(board)
    while not game_is_over and not game_is_won:
        print(board_view(board))
        board = board_revealed_at_cell(ask_cell_num(), board)
        game_is_over = is_game_over(board)
        game_is_won = is_game_won(board)

    print(board_view(board, revealed=True))
    if game_is_over:
        print("You've lost")

    if game_is_won:
        print("You've won")

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
