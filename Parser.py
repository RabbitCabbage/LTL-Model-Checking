class TS_node:
    def __init__(self, ts, index):
        self.ts = ts
        self.index = index
        # next is a list of all the nodes that can be reached from the current node
        # in the form of a pair, (action, next_node_index)
        self.next = []
        self.prev = []
        self.propositions = None

    def add_propositions(self, propositions):
        self.propositions = propositions

    def add_next(self, action, next_node_index):
        self.next.append((action, next_node_index))

    def add_prev(self, action, prev_node_index):
        self.prev.append((action, prev_node_index))

class TS:
    def __init__(self, filename):
        # read from file and store in a list
        self.filename = filename
        self.file = open(filename, 'r')
        self.lines = self.file.readlines()
        self.file.close()

        # get the number of states and transitions
        self.index = 0
        self.current_line = self.lines[self.index]
        self.state_number, self.transition_number = self.current_line.split()
        self.state_number = int(self.state_number)
        self.states = []
        for i in range(self.state_number):
            self.states.append(TS_node(self, i))
        self.transition_number = int(self.transition_number)

        # get the initial states
        self.index += 1
        self.current_line = self.lines[self.index]
        self.initial_state = self.current_line.split()
        self.initial_state = int(self.initial_state[0])
        ############## DEBUG ###############
        # print(self.initial_state)
        ############## DEBUG ###############

        # get the actions and propositions
        self.index += 1
        self.current_line = self.lines[self.index]
        self.actions = self.current_line.split()
        self.index += 1
        self.current_line = self.lines[self.index]
        self.propositions = self.current_line.split()
        ############## DEBUG ###############
        # print(self.actions)
        # print(self.propositions)
        ############## DEBUG ###############

        # get the states, construct a directed graph
        for i in range(self.transition_number):
            self.index += 1
            self.current_line = self.lines[self.index]
            source, action, target = self.current_line.split()
            ############## DEBUG ###############
            # print(source, action, target)
            ############## DEBUG ###############
            source = int(source)
            target = int(target)
            self.states[source].add_next(action, target)
            self.states[target].add_prev(action, source)

        # get the LTL properties of the states
        for i in range(self.state_number):
            self.index += 1
            self.current_line = self.lines[self.index]
            propositions = self.current_line.split()
            for j in range(len(propositions)):
                propositions[j] = self.propositions[int(propositions[j])]
            self.states[i].add_propositions(propositions)
            ############## DEBUG ###############
            # print(i, propositions)
            ############## DEBUG ###############

class Subformula:
    # type: 'until', 'next', 'conjunction', 'negation', 'proposition'
    def __init__(self, type):
        self.type = type

class Until(Subformula):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        super().__init__('until')
    def __str__(self):
        return '(' + str(self.left) + ' U ' + str(self.right) + ')'
    def __eq__(self, other) -> bool:
        return other.type == 'until' and self.left.__eq__(other.left) and self.right.__eq__(other.right)
    def __hash__(self):
        return hash(self.type) + self.left.__hash__() + self.right.__hash__()

class Next(Subformula):
    def __init__(self, formula):
        self.formula = formula
        super().__init__('next')
    def __str__(self):
        return 'X(' + str(self.formula) + ')'
    def __eq__(self, other) -> bool:
        return other.type == 'next' and self.formula.__eq__(other.formula)
    def __hash__(self):
        return hash(self.type) + self.formula.__hash__()

class Conjunction(Subformula):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        super().__init__('conjunction')
    def __str__(self):
        return '(' + str(self.left) + ' /\\ ' + str(self.right) + ')'
    def __eq__(self, other) -> bool:
        return other.type == 'conjunction' and self.left.__eq__(other.left) and self.right.__eq__(other.right)
    def __hash__(self):
        return hash(self.type) + self.left.__hash__() + self.right.__hash__()

class Negation(Subformula):
    def __init__(self, formula):
        self.formula = formula
        super().__init__('negation')
    def __str__(self):
        return '!' + str(self.formula)
    def __eq__(self, other) -> bool:
        return other.type == 'negation' and self.formula.__eq__(other.formula)
    def __hash__(self):
        return hash(self.type) + self.formula.__hash__()
    
class Proposition(Subformula):
    def __init__(self, proposition):
        # propositions and 'true'.
        self.proposition = proposition
        super().__init__('proposition')
    def __str__(self):
        return self.proposition
    def __eq__(self, other) -> bool:
        return other.type == 'proposition' and self.proposition == other.proposition
    def __hash__(self):
        return hash(self.type + self.proposition)

class ParsedFormula:
    # construct the closure and elementary sets of the formula
    def __init__(self, formula_str, alphabet):
        ############## DEBUG ###############
        # print(formula_str)
        ############## DEBUG ###############
        self.alphabet = alphabet
        self.formula_str = formula_str
        # closure is a list of all the subformulae in the closure of the formula
        self.closure = set()
        self.elementary_sets = []
        self.formula = None
        # construct the closure of the formula
        self.get_closure()
        self.get_elementary_sets()

        ############## DEBUG ###############
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print("Closure: ")
        print("[", end='')
        for formula in self.closure:
            print(formula, end=', ')
        print(']\n')
        print("Elementary sets: ")
        for subset in self.elementary_sets:
            print("[", end='')
            for formula in subset:
                print(formula, end=', ')
            print('], ', end='\n')
        print('\n')
        ############## DEBUG ###############

    def get_closure(self) -> None:
        # construct_closure is recursive
        self.formula = self.construct_closure(self.formula_str)
        self.closure.add(self.formula)
        if self.formula.type != 'negation':
            self.closure.add(Negation(self.formula))

    def construct_closure(self, formula_str) -> Subformula:
        ############## DEBUG ###############
        # print("construct from formula_str: ", formula_str)
        ############## DEBUG ###############
        # recursively construct the closure of the formula
        if formula_str[0] == 'X':
            # next
            if formula_str[1] == '(':
                subformula_str = formula_str[2: len(formula_str)-1]
            else :
                subformula_str = formula_str[1:]
            # get the content after the X
            subformula = self.construct_closure(subformula_str)
            self.closure.add(subformula)
            if subformula.type != 'negation':
                self.closure.add(Negation(subformula))
            return Next(subformula)
        
        elif formula_str[0] == 'F':
            # eventually = true until
            if formula_str[1] == '(':
                subformula_str = formula_str[2: len(formula_str)-1]
            else :
                subformula_str = formula_str[1:]
            # get the content after the F
            subformula = self.construct_closure(subformula_str)
            self.closure.add(subformula)
            if subformula.type != 'negation':
                self.closure.add(Negation(subformula))
            self.closure.add(Proposition('true'))
            self.closure.add(Proposition('false'))
            return Until(Proposition('true'), subformula)
        
        elif formula_str[0] == 'G':
            # always = not eventually not
            if formula_str[1] == '(':
                subformula_str = formula_str[2: len(formula_str)-1]
            else :
                subformula_str = formula_str[1:]
            # get the content after the G
            subformula = self.construct_closure(subformula_str)
            self.closure.add(subformula)
            self.closure.add(Proposition('true'))
            self.closure.add(Proposition('false'))
            if subformula.type != 'negation':
                self.closure.add(Negation(subformula))
                self.closure.add(Until(Proposition('true'), Negation(subformula)))
                return Negation(Until(Proposition('true'), Negation(subformula)))
            else:
                # the negation of subformula is subformula.formula
                # which has been added to the closure
                self.closure.add(Until(Proposition('true'), subformula.formula))
                return Negation(Until(Proposition('true'), subformula.formula))
        
        elif formula_str[0] == '!':
            # negation
            if formula_str[1] == '(':
                subformula_str = formula_str[2: len(formula_str)-1]
            else :
                subformula_str = formula_str[1:]
            # get the content after the !
            subformula = self.construct_closure(subformula_str)
            self.closure.add(subformula)
            if subformula.type != 'negation':
                return Negation(subformula)
            else:
                return subformula.formula  
        
        else:
            # traverse the formula with parentheses stack
            stack = []
            balanced_operator = -1
            for i in range(len(formula_str)):
                if len(stack) == 0 and (formula_str[i] == 'U' or formula_str[i] == '/' or formula_str[i] == '\\' or formula_str[i] == '-'):
                    balanced_operator = i
                    break
                if formula_str[i] == '(':
                    stack.append(i)
                elif formula_str[i] == ')':
                    stack.pop()
            if balanced_operator == -1:
                # so all the parentheses are balanced
                if formula_str[0] == '(':
                    subformula_str = formula_str[1: len(formula_str)-1]
                    return self.construct_closure(subformula_str)
                elif formula_str == 'true' or formula_str == 'false' or formula_str in self.alphabet:
                    return Proposition(formula_str)
                else:
                    print("Error: ", formula_str)
                    return None
            elif formula_str[balanced_operator] == 'U':
                lhs_str = formula_str[0: balanced_operator]
                rhs_str = formula_str[balanced_operator+1:]
                if lhs_str[0] == '(':
                    lhs_str = lhs_str[1: len(lhs_str)-1]
                if rhs_str[0] == '(':
                    rhs_str = rhs_str[1: len(rhs_str)-1]
                lhs = self.construct_closure(lhs_str)
                rhs = self.construct_closure(rhs_str)
                self.closure.add(lhs)
                self.closure.add(rhs)
                if lhs.type != 'negation':
                    self.closure.add(Negation(lhs))
                if rhs.type != 'negation':
                    self.closure.add(Negation(rhs))
                return Until(lhs, rhs)
            elif formula_str[balanced_operator] == '/':
                lhs_str = formula_str[0: balanced_operator]
                rhs_str = formula_str[balanced_operator+2:]
                if lhs_str[0] == '(':
                    lhs_str = lhs_str[1: len(lhs_str)-1]
                if rhs_str[0] == '(':
                    rhs_str = rhs_str[1: len(rhs_str)-1]
                lhs = self.construct_closure(lhs_str)
                rhs = self.construct_closure(rhs_str)
                self.closure.add(lhs)
                self.closure.add(rhs)
                if lhs.type != 'negation':
                    self.closure.add(Negation(lhs))
                if rhs.type != 'negation':
                    self.closure.add(Negation(rhs))
                return Conjunction(lhs, rhs)
            elif formula_str[balanced_operator] == '\\':
                lhs_str = formula_str[0: balanced_operator]
                rhs_str = formula_str[balanced_operator+2:]
                if lhs_str[0] == '(':
                    lhs_str = lhs_str[1: len(lhs_str)-1]
                if rhs_str[0] == '(':
                    rhs_str = rhs_str[1: len(rhs_str)-1]
                lhs = self.construct_closure(lhs_str)
                rhs = self.construct_closure(rhs_str)
                self.closure.add(lhs)
                self.closure.add(rhs)
                neg_lhs = None
                neg_rhs = None
                if lhs.type != 'negation':
                    self.closure.add(Negation(lhs))
                    neg_lhs = Negation(lhs)
                else:
                    neg_lhs = lhs.formula
                if rhs.type != 'negation':
                    self.closure.add(Negation(rhs))
                    neg_rhs = Negation(rhs)
                else:
                    neg_rhs = rhs.formula
                self.closure.add(Conjunction(neg_lhs, neg_rhs))
                return Negation(Conjunction(neg_lhs, neg_rhs))
            elif formula_str[balanced_operator] == '-':
                lhs_str = formula_str[0: balanced_operator]
                rhs_str = formula_str[balanced_operator+2:]
                if lhs_str[0] == '(':
                    lhs_str = lhs_str[1: len(lhs_str)-1]
                if rhs_str[0] == '(':
                    rhs_str = rhs_str[1: len(rhs_str)-1]
                lhs = self.construct_closure(lhs_str)
                rhs = self.construct_closure(rhs_str)
                self.closure.add(lhs)
                self.closure.add(rhs)
                neg_rhs = None
                if lhs.type != 'negation':
                    self.closure.add(Negation(lhs))
                if rhs.type != 'negation':
                    self.closure.add(Negation(rhs))
                    neg_rhs = Negation(rhs)
                else:
                    neg_rhs = rhs.formula
                # should return negation a or b
                # return Disjunction(Negation(lhs), rhs)
                self.closure.add(Conjunction(lhs, neg_rhs))
                return Negation(Conjunction(lhs, neg_rhs))
            else:
                print("Error: ", formula_str)
                return None

    # tool function, I should have define it before the construction of closure for convenience, but I am too lazy to modify the code.
    def negation(self, formula) -> Subformula:
        if formula.type == 'negation':
            return formula.formula
        else:
            if formula.type == 'proposition' and formula.proposition == 'true':
                return Proposition('false')
            if formula.type == 'proposition' and formula.proposition == 'false':
                return Proposition('true')
            return Negation(formula)
        
    def get_subsets(self) -> list:
        # get all the subsets of the closure
        closure = list(self.closure)
        subsets = []
        for i in range(1 << len(closure)):
            subset = []
            for j in range(len(closure)):
                if i & (1 << j):
                    subset.append(closure[j])
            subsets.append(subset)
        return subsets
        
    def is_elementary(self, subset) -> bool:
        if Proposition('false') in subset:
                return False
        for formula in self.closure:
            # completeness, maximality
            if not formula in subset and self.negation(formula) not in subset:
                return False
            # consistency
            if self.negation(formula) in subset and formula in subset:
                return False
        ############## DEBUG ###############
        # print('[', end='')
        # for formula in subset:
        #     print(formula, end=', ')
        # print(']')
        ############## DEBUG ###############
        for formula in subset:
            # if a /\ b in subset, then !a or !b should not be in subset
            if formula.type == 'conjunction':
                if self.negation(formula.left) in subset or self.negation(formula.right) in subset:
                    return False
            # if !(a /\ b) in subset, then a and b should not be in subset
            if formula.type == 'negation' and formula.formula.type == 'conjunction':
                if formula.formula.left in subset and formula.formula.right in subset:
                    return False
        # if a U b in subset, then !a and !b should not be in subset
        for formula in subset:
            if formula.type == 'until':
                if self.negation(formula.left) in subset and self.negation(formula.right) in subset:
                    return False
        # if b in subset, then !(a U b) should not be in subset
        for formula in subset:
            for until_formula in self.closure:
                if until_formula.type == 'until' and until_formula.right == formula:
                    if self.negation(until_formula) in subset:
                        return False
        return True
            
    
    def get_elementary_sets(self) -> None:
        # first get all subset of the closure
        subsets = self.get_subsets()
        # then check every subset to see if it is an elementary set
        for subset in subsets:
            if self.is_elementary(subset):
                self.elementary_sets.append(subset)
        return self.elementary_sets