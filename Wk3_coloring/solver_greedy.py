#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import random

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    solution = range(0, node_count)


#    OLD GREEDY SOLUTION
#    ===Description===
# choose the lowest available number for each node
# this got a 22/60 on the website which is insufficient.
# Below is a list of generated vs preferred values (of the max color) for all 6 problems:
# 1. (11, 8)
# 2. (24, 20)
# 3. (21, 16)
# 4. (99, 95)
# 5. (21, 18)
# 6. (127, 124)
# The last problem had 1000 nodes.
# After sorting nodes by degree there was improvement on the last problem only.
#   ===Code===
    for node in range(node_count):
        # check all neighboring nodes and record their numbers
        neighbors = []
        for edge in edges:
            if edge[0] == node:
                neighbors.append(edge[1])
            if edge[1] == node:
                neighbors.append(edge[0])
        # iterate until an available color is found
        color = 0
        local_solution = []
        for neighbor in neighbors:
            local_solution.append(solution[neighbor])
        while (color in local_solution):
            color += 1
        solution[node] = color

    color_count = max(solution) + 1
    # prepare the solution in the specified output format
    output_data = str(color_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

