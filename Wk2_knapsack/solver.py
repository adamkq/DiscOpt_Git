#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import numpy as np
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))
    
    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
##    value = 0
##    weight = 0
##    taken = [0]*len(items)
##
##    for item in items:
##        if weight + item.weight <= capacity:
##            taken[item.index] = 1
##            value += item.value
##            weight += item.weight

    # an optimal algo: using a 2D array to run dynamic programming
    # pseudocode:
    #
    # initialize a 2D array K * J.
    # for each weight from 0 to K:
    #   create a row
    #   for each j value:
    #       if k - w_j > 0:
    #           fill in max([k, j-1],[k - w_j, j - 1])
    #       else:
    #           fill in 0
    #
    # step back. Starting on [K, J]
    # while k > 0:
    #   if [k, j-1] < [k, j]:
    #       taken[j] = 1
    #       go to cell [k - w_j, j-1]
    #   else:
    #       go to cell [k, j-1]
    
    taken = [0]*len(items)
    values = np.array([[0]*(len(items)+1)]*(capacity+1)) # accounts for max-weight and no-item configs

    # build-up
    for k in range(values.shape[0]):
        for i in range(1,values.shape[1]):
            if k - items[i-1].weight >= 0:
                values[k,i] = max(values[k,i-1], values[k-items[i-1].weight,i-1] + items[i-1].value)
            else:
                values[k,i] = values[k,i-1]

    k = capacity
    j = len(items)
    value = 0
    weight = 0
    
    # analysis/backtracking
    while k > 0 and j >= 0:
        if values[k,j] > values[k,j-1]:
            taken[j-1] = 1
            k -= items[j-1].weight
            value += items[j-1].value
            weight += items[j-1].weight
        j -= 1
                
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

