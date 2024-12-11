import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if the length of the set is equal to count of mines then can assume all cells in sentence are mines
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the length of the set is equal to zero then can assume all cells in sentence are safe
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # if cell is a mine remove it from the sentence and update count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # if cell is safe remove it from the sentence.  Count stays same
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # create new set representing board:
        self.board = set()
        for i in range(self.height):
            for j in range(self.width):
                self.board.add((i,j))

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe and update any sentences in knowledge that contain this cell
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # Find neighbouring cells that could be mines and add as a new sentence to knowledge
        
        #  Set to hold adjacent cells
        cells = set()

        # Find all the adjacent cells and put in a set
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Add to cells if cell is in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells.add((i, j))
        
        # check which elements of self.mines are in the adjacent cells set
        neighbour_mines = cells.intersection(self.mines)

        # remove any cells from set of neighbours with known state
        cells.difference_update(self.mines)
        cells.difference_update(self.safes)

        # the number of mines in the set of adjacent cells is
        count_mines = count - len(neighbour_mines)
        
        # Add a new sentence to knowledge containing the neighbouring cells and count of mines
        self.knowledge.append(Sentence(cells, count_mines))

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        safe_cells = set()
        mine_cells = set()

        for sentence in self.knowledge:
            safe_cells.update(sentence.known_safes())
            mine_cells.update(sentence.known_mines())
        
        # Update knowledge base
        for cell in safe_cells:
            self.mark_safe(cell)
        
        for cell in mine_cells:
            self.mark_mine(cell)

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        self.infer_new_knowledge()
        
    def infer_new_knowledge(self):
        """
        Called by add_knowledge method
        iterates over sentences in knowledge and checks if any new mines
        or safes can be identified or any new sentences inferred
        """

        safe_cells = set()
        mine_cells = set()
        new_sentences = []

        for sentence in self.knowledge:
            # check each sentance against others
            for comparator in self.knowledge:
                # check if sentence is a subset of comparator
                if sentence.cells.issubset(comparator.cells):
                    new_sentence = comparator.cells.difference(sentence.cells)
                    mines = comparator.count - sentence.count
                    if mines == 0:
                        for cell in new_sentence:
                            safe_cells.add(cell)
                    elif len(new_sentence) == mines:
                        for cell in new_sentence:
                            mine_cells.add(cell)
                    else:
                        new_sentences.append(Sentence(new_sentence, mines))
                # check if comparator is a subset of sentence
                elif comparator.cells.issubset(sentence.cells):
                    new_sentence = sentence.cells.difference(comparator.cells)
                    mines = sentence.count - comparator.count
                    if mines == 0:
                        for cell in new_sentence:
                            safe_cells.add(cell)
                    elif len(new_sentence) == mines:
                        for cell in new_sentence:
                            mine_cells.add(cell)
                    else:
                        new_sentences.append(Sentence(new_sentence, mines))

        # Update knowledge base
        for cell in safe_cells:
            self.mark_safe(cell)
        
        for cell in mine_cells:
            self.mark_mine(cell)
        
        self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_set = self.safes.difference(self.moves_made, self.mines)
        if safe_set:
            return safe_set.pop()
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # choose a random cell amongst unknowns
        unknowns = self.board.difference(self.moves_made, self.mines)
        if unknowns:
            return random.choice(list(unknowns))
        else:
            return None