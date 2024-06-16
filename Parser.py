class node:
    def __init__(self, index):
        self.index = index
        # next is a list of all the nodes that can be reached from the current node
        # in the form of a pair, (action, next_node_index)
        self.next = []
        self.prev = []

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
            self.states.append(node(i))
        self.transition_number = int(self.transition_number)

        # get the initial states
        self.index += 1
        self.current_line = self.lines[self.index]
        self.initial_state = self.current_line.split()
        self.initial_state = int(self.initial_state[0])
        print(self.initial_state)

        # get the actions and propositions
        self.index += 1
        self.current_line = self.lines[self.index]
        self.actions = self.current_line.split()
        self.index += 1
        self.current_line = self.lines[self.index]
        self.propositions = self.current_line.split()
        print(self.actions)
        print(self.propositions)

        # get the states, construct a directed graph
        for i in range(self.transition_number):
            self.index += 1
            self.current_line = self.lines[self.index]
            source, action, target = self.current_line.split()
            print(source, action, target)
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
            print(i, propositions)

def dfs_always(ts, state_idx, formula):
    visited = []
    visited.append(state_idx)
    stack = []
    stack.append(state_idx)
    while stack:
        node = stack.pop()
        if not check_formulae(ts, node, formula):
            return False
        for next in ts.states[node].next:
            if next[1] not in visited:
                visited.append(next[1])
                stack.append(next[1])
    return True

def dfs_eventually(ts, state_idx, formula):
    visited = []
    visited.append(state_idx)
    stack = []
    stack.append(state_idx)
    while stack:
        node = stack.pop()
        if check_formulae(ts, node, formula):
            return True
        for next in ts.states[node].next:
            if next[1] not in visited:
                visited.append(next[1])
                stack.append(next[1])
    return False

def dfs_until(ts, state_idx, lhs, rhs):
    visited = []
    visited.append(state_idx)
    stack = []
    stack.append(state_idx)
    while stack:
        node = stack.pop()
        if check_formulae(ts, node, rhs):
            return True
        elif not check_formulae(ts, node, lhs):
            return False
        for next in ts.states[node].next:
            if next[1] not in visited:
                visited.append(next[1])
                stack.append(next[1])
    return False

# check the formulae on the TS recursively
def check_formulae(ts, state_idx, formula):
    print(state_idx, formula)
    node = ts.states[state_idx]
    if formula[0] == 'X':
        # check all the next states
        if formula[1] == '(':
            subformula = formula[2: len(formula)-1]
        else :
            subformula = formula[1:]
        for next in node.next:
            if check_formulae(ts, next[1], subformula):
                return True
            else:
                return False
    
    elif formula[0] == 'G':
        # always, so dfs until a false is found or loop
        if formula[1] == '(':
            subformula = formula[2: len(formula)-1]
        else :
            subformula = formula[1:]
        return dfs_always(ts, state_idx, subformula)
    
    elif formula[0] == 'F':
        # eventually, so dfs until a true is found or loop
        if formula[1] == '(':
            subformula = formula[2: len(formula)-1]
        else :
            subformula = formula[1:]
        return dfs_eventually(ts, state_idx, subformula)
    
    elif formula[0] == '!':
        # not, so return the negation of the formula
        if formula[1] == '(':
            subformula = formula[2: len(formula)-1]
        else :
            subformula = formula[1:]
        return not check_formulae(ts, state_idx, subformula)
    
    else:
        # traverse the formula with parentheses stack
        stack = []
        balanced_operator = -1
        for i in range(len(formula)):
            if len(stack) == 0 and (formula[i] == 'U' or formula[i] == '/' or formula[i] == '\\' or formula[i] == '-'):
                balanced_operator = i
                break
            if formula[i] == '(':
                stack.append(i)
            elif formula[i] == ')':
                stack.pop()
    if balanced_operator == -1:
        # so all the parentheses are balanced
        if formula[0] == '(':
            subformula = formula[1: len(formula)-1]
            return check_formulae(ts, state_idx, subformula)
        elif len(formula) == 1:
            # proposition, so return the value of the proposition
            return formula in node.propositions 
        else:
            # may be an error
            print("Error in formula: ", formula)
            return False

    elif formula[balanced_operator] == 'U':
        # until, so dfs until a true is found or loop
        sublhs = formula[0: formula.find('U')]
        subrhs = formula[formula.find('U')+1: len(formula)]
        # remove the parentheses and space, if there are any
        if sublhs[0] == '(':
            sublhs = sublhs[1: len(sublhs)-1]
        if subrhs[0] == '(':
            subrhs = subrhs[1: len(subrhs)-1]
        return dfs_until(ts, state_idx, sublhs, subrhs)

    elif formula[balanced_operator] == '-':
        # implies, so return the implication of the two formulae
        sublhs = formula[0: formula.find('->')]
        subrhs = formula[formula.find('->')+2: len(formula)]
        # remove the parentheses and space, if there are any
        if sublhs[0] == '(':
            sublhs = sublhs[1: len(sublhs)-1]
        if subrhs[0] == '(':
            subrhs = subrhs[1: len(subrhs)-1]
        return not check_formulae(ts, state_idx, sublhs) or check_formulae(ts, state_idx, subrhs)
    
    elif formula[balanced_operator] == '/':
        # and, so return the conjunction of the two formulae
        sublhs = formula[0: formula.find('/\\')]
        subrhs = formula[formula.find('/\\')+2: len(formula)]
        # remove the parentheses and space, if there are any
        if sublhs[0] == '(':
            sublhs = sublhs[1: len(sublhs)-1]
        if subrhs[0] == '(':
            subrhs = subrhs[1: len(subrhs)-1]
        return check_formulae(ts, state_idx, sublhs) and check_formulae(ts, state_idx, subrhs)

    elif formula[balanced_operator] == '\\':
        # or, so return the disjunction of the two formulae
        sublhs = formula[0: formula.find('\\/')]
        subrhs = formula[formula.find('\\/')+2: len(formula)]
        # remove the parentheses and space, if there are any
        if sublhs[0] == '(':
            sublhs = sublhs[1: len(sublhs)-1]
        if subrhs[0] == '(':
            subrhs = subrhs[1: len(subrhs)-1]
        return check_formulae(ts, state_idx, sublhs) or check_formulae(ts, state_idx, subrhs)


        
ts = TS("TS.txt")
file = open("benchmark1.txt", 'r')
lines = file.readlines()
file.close()
from_init, from_other = lines[0].split()
from_init = int(from_init)
from_other = int(from_other)

formulae = []
for i in range(from_init):
    formulae.append((ts.initial_state, lines[i+1].split('\n')[0].replace(' ', '')))
for i in range(from_other):
    formulae.append((int(lines[from_init+i+1].split()[0]), lines[from_init+i+1].split(' ', 1)[1].split('\n')[0].replace(' ', '')))
print(formulae)
list = []
for formula in formulae:
    list.append(check_formulae(ts, formula[0], formula[1]))

print(list)
