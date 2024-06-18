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
                # find nba_node having the same propositions
                for nba_node_idx_pair in nba.nodes:
                    nba_node = nba.nodes[nba_node_idx_pair]
                    # edge: 
                    ############## DEBUG ###############
                    print('-------------------------')
                    print('nba node: ', nba_node.propositions)
                    print('ts state: ', prop_set)
                    print(prop_set.issubset(set(nba_node.propositions)))
                    ############## DEBUG ###############
                    if 'true' in nba_node.propositions or prop_set.issubset(set(nba_node.propositions)):
                        self.nodes[(ts_node.index, nba_node_idx_pair)].add_next(action, (next_ts_node.index, nba_node_idx_pair))
        self.init = []
        ts_init_state = ts.states[ts.initial_state]
        prop_set = set(ts_init_state.propositions)
        for nba_node_idx_pair in nba.nodes:
            nba_node = nba.nodes[nba_node_idx_pair]
            if prop_set == set(nba_node.propositions):
                self.init.append((ts.initial_state, nba_node_idx_pair))
    
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
        for init_idx in self.init:
            if init_idx in outer_visited:
                continue
            init_node = self.nodes[init_idx]
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
                    if cur_node.new_prop in self.nba.final:
                        cycle_found = self.on_cycle(cur_node)
                else:
                    outer_stack.append(next_node)
                    outer_visited.append(index_triple)
        # if cycle found, it means there is a reachable cycle with final state, return True
        return cycle_found


            