from Parser import *
from GNBA import *
from NBA import *
from Product import *


ts = TS("../benchmark/TS.txt")
# filename_list = ['../doc/ds_debug.txt']
filename_list = ['../benchmark/sample.txt', '../benchmark/benchmark.txt','../benchmark/benchmark1.txt']
for file_name in filename_list:
    file = open(file_name, 'r')
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
        # print('===========================')
        # print(formula_str)
        ############## DEBUG ###############

        ts.initial_state = formula_str[0]
        es = ParsedFormula('!('+formula_str[1]+')', ts.propositions)
        gnba = GNBA(ts.propositions, '!('+formula_str[1]+')', es)

        ############## DEBUG ###############
        # print("closure: [")
        # for i in es.closure:
        #     print(i)
        # print("]")
        # print("GNBA initial: ", gnba.initial)
        # print("GNBA final: ", gnba.final)
        # gnba.print_gnba()
        ############## DEBUG ###############

        nba = NBA(gnba)
        product = Product(ts, nba)

        ############## DEBUG ###############
        # print('product initial: ', product.init)
        # print('nba initial: ', nba.initial)
        # print('nba final: ', nba.final)
        ############## DEBUG ###############
        
        # list.append(product.persistence_check())
        if product.persistence_check():
            list.append(1)
        else:
            list.append(0)

    print(list)