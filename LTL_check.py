from Parser import *
from GNBA import *
from NBA import *
from Product import *


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
# print(formulae)

list = []
for formula_str in formulae:
    ############## DEBUG ###############
    print('===========================')
    print(formula_str)
    ############## DEBUG ###############
    es = ParsedFormula(formula_str[1], ts.propositions)
    gnba = GNBA(ts.propositions, formula_str[1], es)
    ############## DEBUG ###############
    print("GNBA initial: ", gnba.initial)
    print("GNBA final: ", gnba.final)
    ############## DEBUG ###############
    gnba.print_gnba()
    nba = NBA(gnba)
    product = Product(ts, nba)
    list.append(product.persistence_check())

print(list)