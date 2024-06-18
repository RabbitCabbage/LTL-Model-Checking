from GNBA import GNBA_node
from GNBA import GNBA

class NBA_node:
    def __init__(self, gnba_node, gnba_index, gnba_node_index):
        self.formula_set = gnba_node.formula_set
        self.propositions = gnba_node.propositions
        self.gnba_index = gnba_index
        self.gnba_node_index = gnba_node_index
        self.next = set()
    
    def add_next(self, gnba_index, gnba_node_index):
        self.next.add((gnba_index, gnba_node_index))


class NBA:
    def __init__(self, gnba):
        self.gnba = gnba
        # nodes is a map from (gnba_index, gnba_node_index) to nba_node
        self.nodes = {}
        self.final_number = len(self.gnba.final)
        for final_idx in range(len(self.gnba.final)):
            for gnba_node_idx in range(len(self.gnba.nodes)):
                gnba_node = self.gnba.nodes[gnba_node_idx]
                nba_node = NBA_node(gnba_node, final_idx, gnba_node_idx)
                if gnba_node_idx in self.gnba.final[final_idx]:
                    # connect with nodes in next gnba
                    for next_idx in gnba_node.next:
                        nba_node.add_next((final_idx+1)%self.final_number, next_idx)
                else:
                    # connect with nodes in this gnba
                    for next_idx in gnba_node.next:
                        nba_node.add_next(final_idx, next_idx)
                self.nodes[(final_idx, gnba_node_idx)] = nba_node
        # list of (gnba_index, gnba_node_index) to represent initial nodes and final nodes
        self.initial = []
        for idx in self.gnba.initial:
            self.initial.append((0, idx))
        self.final = []
        if not len(gnba.final) == 0:
            for idx in gnba.final[0]:
                self.final.append((0, idx))
            