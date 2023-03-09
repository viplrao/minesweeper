import random


class Minesweeper():  # Pre-Written
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

    # Pre-Written
    def __init__(self, cells: set, count: int):
        self.cells = set(cells)
        self.count = count

    # Pre-Written
    def __eq__(self, other) -> bool:
        return self.cells == other.cells and self.count == other.count

    # Pre-Written
    def __str__(self) -> str:
        return f"{self.cells} = {self.count}"

    def known_mines(self) -> set:
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # {1,2,3} = 3? Then all mines else we don't know anything
        return self.cells if self.count == len(self.cells) and self.count != 0 else set()

    def known_safes(self) -> set:
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Either we know there are no mines in the set (c=0) or we know nothing
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)  # Remove the cell from the sentence
            self.count -= 1      # Decrement the no. of Mines

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)  # Remove the cell from the sentence
            # No need to decrement for safe cells


class MinesweeperAI():
    """
    Minesweeper game player
    """

    # Pre-Written
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

    # Pre-Written
    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    # Pre-Written
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
        # 1), 2)
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # 3)
        # Find all neighboring cells
        neighborhood = [(x, y) for x in range(cell[0] - 1, cell[0] + 2) if x >= 0 and x < self.width
                        for y in range(cell[1] - 1, cell[1] + 2) if y >= 0 and y < self.height]

        # Parse data
        neighborhood_parsed = neighborhood.copy()  # don't edit what you iterate
        for x, y in neighborhood:
            # Trim down the ones we know ARE NOT mines
            if (x, y) == cell or (x, y) in self.safes:
                neighborhood_parsed.remove((x, y))
            # Remove the ones we know ARE mines, update count for inference
            if (x, y) in self.mines:
                neighborhood_parsed.remove((x, y))
                count -= 1

        # Of those cleaned cells, $count are mines - put it in
        print(
            f"Determined {neighborhood_parsed} = {count} from move {cell}")
        self.knowledge.append(Sentence(neighborhood_parsed, count))

        # 4)
        # Don't edit what you iterate pt 2 (For step 5)
        new_knowledge = self.knowledge.copy()
        for sentence_1 in self.knowledge:
            # Don't edit what you iterate pt 3
            init_mines = sentence_1.known_mines().copy()
            init_safes = sentence_1.known_safes().copy()
            for mine in init_mines:
                self.mark_mine(mine)
                print(f"Marked mine: {mine}")
            for safe in init_safes:
                self.mark_safe(safe)
                print(f"Marked safe: {safe}")
            # 5)
            # If sentence s1 is a subset of sentence s2, s2-s1 = c2-c1
            for sentence_2 in self.knowledge:
                if sentence_1 == sentence_2:
                    continue
                if sentence_1.cells.issubset(sentence_2.cells):
                    new_sentence = Sentence(
                        (sentence_2.cells - sentence_1.cells), sentence_2.count - sentence_1.count)
                    if new_sentence not in self.knowledge:
                        new_knowledge.append(new_sentence)
        self.knowledge = new_knowledge

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Don't do more work than you have to
        if len(self.safes) == 0:
            return None
        # Just pick the first safe option
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Make sure all options are good (how's THAT for a list comprehension?)
        good_moves = [(x, y) for x in range(self.height) for y in range(
            self.width) if (x, y) not in self.moves_made and (x, y) not in self.mines]
        # Sometimes there's no way out...
        if len(good_moves) == 0:
            return None
        # If there is one though, just pick randomly
        return random.choice(good_moves)
