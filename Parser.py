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



ts = TS("TS.txt")
file = open("sample.txt", 'r')
lines = file.readlines()
file.close()
from_init, from_other = lines[0].split()
from_init = int(from_init)
from_other = int(from_other)

formulae = []
for i in range(from_init):
    formulae.append((ts.initial_state, lines[i+1]))
for i in range(from_other):
    formulae.append((int(lines[from_init+i+1].split()[0]), lines[from_init+i+1].split(' ', 1)[1]))
print(formulae)

# check the formulae on the TS recursively