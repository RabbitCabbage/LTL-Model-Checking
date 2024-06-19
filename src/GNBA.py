from Parser import ParsedFormula
from Parser import Subformula
from Parser import Until
from Parser import Proposition
from Parser import Conjunction
from Parser import Negation
from Parser import Next

class GNBA_node:
    def __init__(self, formula_str, formula_set, alphabet):
        self.formula_str = formula_str
        self.formula_set = formula_set
        self.next = set()
        self.alphabet = alphabet
        # prop as condition on the edge of outdegree.
        self.propositions = []
        for formula in formula_set:
            if formula.type == 'proposition' and formula.proposition != 'true' and formula.proposition != 'false':
                self.propositions.append(formula.proposition)

    def add_next(self, node_idx):
        self.next.add(node_idx)

    def __str__(self) -> str:
        str = "[\n"
        for formula in self.formula_set:
            str += formula.__str__() + ",\n"
        str = str + "]\nprops: ["
        for prop in self.propositions:
            str += prop + ", "
        return str + "]"


class GNBA:
    def __init__(self, alphabet, formula_str, parsed_formula):
        self.formula_str = formula_str
        # list of nodes
        self.nodes = []
        # list of indices of nodes
        self.initial = []
        self.final = []
        self.alphabet = alphabet
        self.parsed_formula = parsed_formula
        self.build_gnba()

    def build_gnba(self):
        # build nodes from pased formula
        # for formula_set in self.parsed_formula.elementary_set:
        for index in range(len(self.parsed_formula.elementary_sets)):
            formula_set = self.parsed_formula.elementary_sets[index]
            node = GNBA_node(self.formula_str, formula_set, self.alphabet)
            self.nodes.append(node)
            if self.parsed_formula.formula in formula_set:
                self.initial.append(index)
        
        # every until formula in closure is related with a final set.
        for until in self.parsed_formula.closure:
            if until.type == 'until':
                F = []
                # for formula_set in self.parsed_formula.elementary_set:
                for index in range(len(self.parsed_formula.elementary_sets)):
                    formula_set = self.parsed_formula.elementary_sets[index]
                    # if this set satisfies the until formula
                    # if not (until.left not in formula_set and until.right not in formula_set):
                    if not (until in formula_set and until.right not in formula_set):
                        F.append(index)
                self.final.append(F)
        # for final_set in self.final:
        #     # for every pair of nodes in the same final set, add edges
        #     for i in range(len(final_set)):
        #         for j in range(len(final_set)):
        #             self.nodes[final_set[i]].add_next(final_set[j])

        # build edges
        for index in range(len(self.nodes)):
            node = self.nodes[index]
            # add self loop
            # node.add_next(index)
            # keep a list of neg_next, next step should not contain these
            neg_next = []
            for formula in node.formula_set:
                if formula.type == 'negation' and formula.formula.type == 'next':
                    # next node should not contain formula.formula.formula
                    neg_next.append(formula.formula.formula)
                elif formula.type == 'negation' and formula.formula.type == 'until':
                    # (p1 U p2 not in B) iff ((p2 not in B) and ((p1 not in B) or (p1 U p2 not in B))
                    # in which (p2 not in B) holds naturally in elementary set
                    if formula.formula.left in node.formula_set:
                        neg_next.append(formula.formula)

            must_next = []
            for formula in node.formula_set:
                if formula.type == 'next':
                    # next node must contain formula.formula
                    must_next.append(formula.formula)
                elif formula.type == 'until':
                    if formula.right in node.formula_set:
                        continue
                    else:
                        # right is not in this, so next node must contain this until formula
                        must_next.append(formula)
              
            for jndex in range(len(self.nodes)):
                psb_next = self.nodes[jndex]
                # psb_next should not contain negation of next formula
                if not set(neg_next).isdisjoint(psb_next.formula_set):
                    continue
                # psb_next must contain must_next
                if not set(must_next).issubset(psb_next.formula_set):
                    continue
                node.add_next(jndex)

    def print_gnba(self):
        for index in range(len(self.nodes)):
            node = self.nodes[index]
            print("Node", index, ":", node)
            print("Next:", node.next)
            print("")