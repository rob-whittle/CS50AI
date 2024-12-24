import sys
import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            for word in self.crossword.words:
                if variable.length != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # print("Revise called for:", x, y)
        # print("  Before Revision - Domain of x:", self.domains[x], "Domain of y:", self.domains[y])
        # if overlap a pair of ints (i,j) is returned indicating x(i) overlaps y(j)
        overlaps = self.crossword.overlaps[x, y]
        i = overlaps[0]
        j = overlaps[1]

        if overlaps is not None:
            # we must check for any words that don't have same letter at (i,j)
            # we need to create a copy of x words as it is a view on the
            # domains dict and we update it in the loop
            x_words = self.domains[x].copy()
            y_words = self.domains[y]

            for x_word in x_words:
                matches = False  # track if we find a match
                for y_word in y_words:
                    if x_word[i] == y_word[j]:
                        matches = True
                        # can stop after first match and move to next x_word
                        continue
                if not matches:
                    # remove the word if no possible match
                    self.domains[x].remove(x_word)
            # print("  After Revision - Domain of x:", self.domains[x], "Domain of y:", self.domains[y])
            return True

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # print(f'**************new check for arcs: {arcs}')
        if arcs is None:
            arcs = []
            for variable in self.crossword.variables:
                # find the variables neighbours
                neighbors = self.crossword.neighbors(variable)
                # add arcs for this variable to arc list as (x,y) tuple
                arcs.extend([(variable, n) for n in neighbors])

        while arcs:
            # pop first item from arcs queue
            x, y = arcs.pop(0)
            # print(f'x is {x}, y is {y}')
            # if possible to revise the domain
            if self.revise(x, y):
                # if revision results in empty domain return False
                if not self.domains[x]:
                    return False
                # if revised domain not empty need to check other neighbours
                # are still consistent with arc[0]. Get remaining neighbors
                # and add to arcs queue, this time as (n,x) tuple
                for n in self.crossword.neighbors(x):
                    if n != y:
                        arcs.append((n, x))

        # once the arcs queue is exhausted we can return True
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.crossword.variables) == len(assignment):
            # check each variable in assignment has a string assigned
            return all(isinstance(value, str) for value in assignment.values())
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # that is to say, all values are distinct, every value is the correct
        # length, and there are no conflicts between neighboring variables.

        # check values are unique by putting in a set and checking length
        if len(assignment) != len(set(assignment.values())):
            return False

        # check words fit
        for variable, word in assignment.items():
            if variable.length != len(word):
                return False
            # check for conflicts
            for n in self.crossword.neighbors(variable):
                if n in assignment:
                    i, j = self.crossword.overlaps[variable, n]
                    # check letter match at overlaps
                    if word[i] != assignment[n][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # create a new dict to track how many options for neighboring values
        # each word rules out
        heuristic = dict.fromkeys(self.domains[var], 0)

        # Find unassigned neighbors and check overlap
        # Check each word in var's domain to see how many options it rules out
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                for word in self.domains[var]:
                    for neighbor_word in self.domains[neighbor]:
                        if word[i] != neighbor_word[j]:
                            heuristic[word] += 1
        # sort the dictionary on the value, using dictionary.get
        # this method returns value from dict
        return sorted(heuristic, key=heuristic.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        selected = random.choice(list(unassigned))
        for variable in unassigned:
            if len(self.domains[variable]) < len(self.domains[selected]):
                # choose var with smallest domain
                selected = variable
            elif len(self.domains[variable]) == len(self.domains[selected]) and len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(selected)):
                selected = variable

        return selected

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        # select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # check for a word that fits constraints
        for word in self.order_domain_values(var, assignment):
            assignment.update({var: word})
            # if this word is consistent then recursively call
            # backtrack to check remaining variables in space
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                # if result is None remove the assignment
                # loop will try next word in domain
                if result is None:
                    del assignment[var]
                # otherwise break loop through this variables domain
                else:
                    return assignment
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
