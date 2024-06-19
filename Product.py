from Parser import TS
from Parser import TS_node
from NBA import NBA
from GNBA import GNBA
from NBA import NBA_node
from GNBA import GNBA_node

class Product_node:
    def __init__(self, ts_node, nba_node):
        self.ts_node = ts_node
        self.nba_node = nba_node
        self.nodes = {} # indexed by ts_node_index + nba_index_pair
        self.next = set()
        # in product the new AP' is Q, i.e. the set of nba nodes
        # so now L(product_node)=L([ts_node, nba_node])={nba_node}
        # and nba_node can be represented by an index pair
        self.new_prop = (nba_node.gnba_index, nba_node.gnba_node_index)

    def add_next(self, action, index_triple):
        self.next.add((action, index_triple))

class Product:
    def __init__(self, ts, nba):
        self.ts = ts
        self.nba = nba
        self.nodes = {}
        # construct all product nodes
        for ts_node in ts.states:
            for nba_node_idx_pair in nba.nodes:
                nba_node = nba.nodes[nba_node_idx_pair]
                product_node = Product_node(ts_node, nba_node)
                self.nodes[(ts_node.index, nba_node_idx_pair)] = product_node  
        # construct edges between product nodes
        for ts_node in ts.states:
            for (action, next_ts_node_index) in ts_node.next:
                next_ts_node = ts.states[next_ts_node_index]
                prop_set = set(next_ts_node.propositions)
                closure_prop_set = set()
                closure = nba.gnba.parsed_formula.closure
                for formula in closure:
                    if formula.type ==  'proposition' and formula.proposition != 'true' and formula.proposition != 'false' and formula.proposition in prop_set:
                            closure_prop_set.add(formula.proposition)
                # find nba_node having the same propositions
                for nba_node_idx_pair in nba.nodes:
                    nba_node = nba.nodes[nba_node_idx_pair]
                    # edge: 
                    ############## DEBUG ###############
                    # print('-------------------------')
                    # print('nba node: ', nba_node.propositions)
                    # print('ts state: ', prop_set)
                    # print(prop_set.issubset(set(nba_node.propositions)))
                    print("TS EDGE: ", ts_node.index, next_ts_node_index)
                    print('ts state: ', prop_set)
                    print('closure_prop_set: ', closure_prop_set)  
                    print('nba node: ', set(nba_node.propositions))
                    ############## DEBUG ###############
                    if closure_prop_set == set(nba_node.propositions):
                        # self.nodes[(ts_node.index, nba_node_idx_pair)].add_next(action, (next_ts_node.index, nba_node_idx_pair))
                        # all the next of nba_node should be added as edge
                        for next_nba_idx_pair in nba_node.next:
                            self.nodes[(ts_node.index, nba_node_idx_pair)].add_next(action, (next_ts_node.index, next_nba_idx_pair))
                            ############## DEBUG ###############
                            print("NBA EDGE: ", nba_node_idx_pair[1], next_nba_idx_pair[1])
                            ############## DEBUG ###############
        self.init = set()
        ts_init_state = ts.states[ts.initial_state]
        ############## DEBUG ###############
        # print("TS initial state: ", ts_init_state.index)
        # print("TS initial state propositions: ", ts_init_state.propositions)
        # print("NBA initial state: ", nba.initial)
        # for nba_init_idx_pair in nba.initial:
        #     print("NBA initial state propositions: ", nba.nodes[nba_init_idx_pair].propositions)
        ############## DEBUG ###############
        prop_set = set(ts_init_state.propositions)
        closure_prop_set = set()
        closure = nba.gnba.parsed_formula.closure
        for formula in closure:
            if formula.type == 'proposition' and formula.proposition != 'true' and formula.proposition != 'false' and formula.proposition in prop_set:
                    closure_prop_set.add(formula.proposition)
        for nba_node_idx_pair in nba.initial:
            nba_node = nba.nodes[nba_node_idx_pair]
            ############## DEBUG ###############
            # print("NBA initial state propositions: ", nba_node.propositions)
            # print("TS initial state propositions: ", closure_prop_set)
            ############## DEBUG ###############
            if closure_prop_set == set(nba_node.propositions):
                for next_nba_idx_pair in nba_node.next:
                    self.init.add((ts.initial_state, next_nba_idx_pair))
    
    def on_cycle(self, node) -> bool:
        inner_visited = []
        inner_stack = []
        inner_stack.append(node)
        inner_visited.append((node.ts_node.index, node.new_prop))
        while len(inner_stack) > 0:
            cur_node = inner_stack[0]
            # if cur_node can return to node, then cycle found
            for (action, index_triple) in cur_node.next:
                if (node.ts_node.index, node.new_prop) == index_triple:
                    return True
            # else continue DFS
            next_node = None
            for (action, index_triple) in cur_node.next:
                if index_triple in inner_visited:
                    continue
                next_node = self.nodes[index_triple]
                break
            if next_node == None:
                # all next nodes are visited, remove cur_node from stack
                inner_stack.pop(0)
            else:
                inner_stack.append(next_node)
                inner_visited.append(index_triple)
        return False

    def persistence_check(self):
        outer_visited = []
        outer_stack = []
        cycle_found = False
        # path starts at initial state is reachable
        if len(self.init) == 0:
            return True
        while len(self.init.intersection(set(outer_visited))) < len(self.init) and not cycle_found:
            init_idx = None
            for i in self.init:
                if i not in outer_visited:
                    init_idx = i
                    break
            init_node = self.nodes[init_idx]        
            ########### reachable cycle ###########
            outer_stack.append(init_node)
            outer_visited.append(init_idx)
            # start DFS from init_node
            while len(outer_stack) > 0 and not cycle_found:
                cur_node = outer_stack[0]
                next_node = None
                for (action, index_triple) in cur_node.next:
                    if index_triple in outer_visited:
                        continue
                    next_node = self.nodes[index_triple]
                    break
                if next_node == None:
                    # remove cur_node from stack
                    outer_stack.pop(0)
                    # if cur_node is !\Phi, then check if cur_node is on the cycle
                    # print("possible cycle node")
                    if cur_node.new_prop in self.nba.final:
                        cycle_found = self.on_cycle(cur_node)
                else:
                    outer_stack.append(next_node)
                    outer_visited.append(index_triple)
            #########################################

            # ############## DEBUG ###############
            # print("self.init: ", self.init)
            # print("outer_visited: ", outer_visited)
            # print("intersection: ", self.init.intersection(set(outer_visited)))
            # ############## DEBUG ###############

        # if cycle found, it means there is a reachable cycle with final state, return True
        return not cycle_found