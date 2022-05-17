import sys

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
                        w, h = draw.textsize(letters[i][j], font=font)
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

        # iterate over the variables:
        for variable in self.domains.keys():

            # iterate over a copy of the variable to remove x!
            for x in self.domains[variable].copy():

                # if the length of the word x is not equal to length of variable, remove x from original domain
                if len(x) != variable.length:
                    self.domains[variable].remove(x)

        """"# test revise DELETE later:
        k = 0
        for variable in self.domains.keys():
            k += 1
            if k > 2:
                self.arcs(variable_before, variable)
            variable_before = variable
        """

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # set initial status of changes to false
        changed = False
        i, j = self.crossword.overlaps[x, y]

        # loop through words in domain of X and domain of Y. Loop over y first to keep y consistent.
        for word_x in self.domains[x].copy():
            remove = True
            for word_y in self.domains[y].copy():

                # check if any ith character of any wordin x equals any jth character of y
                if word_x[i] == word_y[j]:
                    remove = False
            if remove:
                self.domains[x].remove(word_x)
                changed = True
        # return if there was a change
        return changed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        function AC-3(csp):

            if size of X.domain == 0: return false
            for each Z in X.neighbors - {Y}: ENQUEUE(queue, (Z, X))
        return true
        """
        # check if arcs is none:
        if arcs is None:
            queue = list()

            # Loop over X variable in self.domain and check for neighbors. if neighbor, add arc (x,y) to the queue
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    queue.append((x, y))

        # if not, then queue is equal to arcs
        else:
            queue = arcs

        # check whether there is elements in queue
        while queue:

            # take out first arc (x, y)
            x, y = queue.pop()

            # check if revision was made
            if self.revise(x, y):

                # check if there is no x
                if not self.domains[x]:
                    return False

                # add all new neighbor pairs to the queue
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((x, z))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return not bool(self.crossword.variables - set(assignment))

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        The consistent function should check to see if a given assignment is consistent.
        """

        value_buffer = list()
        for key in assignment:

            # check if value already in buffer (value not distinct) if so, return false
            if assignment[key] not in value_buffer:
                value_buffer.append(assignment[key])
            else:
                return False


            # check if value is correct length
            if len(assignment[key]) != key.length:
                return False

            #if all good, append value to buffer for check


            # check neighbors first loop over neighbors of each key:
            for neighbor in self.crossword.neighbors(key):

                # check whether neighbor is in the assignment
                if neighbor in assignment:

                    # check whether ith character of key variable equals jth character of neighbor variable. otherwise return false
                    i, j = self.crossword.overlaps[key, neighbor]
                    if assignment[key][i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # create empty list to store values:
        list = dict()

        for value in self.domains[var]:
            list[value] = 0
            for neighbor in self.crossword.neighbors(var) - assignment:
                if value in self.domains[neighbor]:
                    n[value] += 1
        return sorted(list, key=list.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = None

        for variable in self.crossword.variables - set(assignment):
            if (
                unassigned_var is None or
                len(self.domains[variable]) < len(self.domains[unassigned_var]) or
                len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(unassigned_var))
                ):
                unassigned_var = variable
        return unassigned_var


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        function Backtrack(assignment, csp):
        """
        #if assignment is complete, return
        if self.assignment_complete(assignment):
            return assignment

        # select an unassigned variable and add it to assignment.
        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            assignment[var] = value

            # check if assignment is consistent. if so, loop over assigment, else remove variable from assignmnent
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)

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
