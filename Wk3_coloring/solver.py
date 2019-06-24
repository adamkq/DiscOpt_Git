#!/usr/bin/python
# -*- coding: utf-8 -*-


#The purpose of this assignment is to find a solution to the graph coloring problem (minimize total number of colors, known as the 'chromatic number'; adjacent nodes must be of different color). This problem runs in exponential time so may not be realistically brute forced to find the 'optimal' solution. The solution must be better than the 'greedy' solution (i.e. for each node, pick the lowest available color, and add an extra color when you run out of colors). I used a Contraint Programming-based method to achieve this, which is described in the code comments.

import math

def build_graph_neighbors(node_count, edges):  # only called once
    graph_neighbor = []
    for node in range(0, node_count):
        neighbors = []
        for edge in edges:
            if edge[0] == node:
                neighbors.append(edge[1])
            if edge[1] == node:
                neighbors.append(edge[0])
        # since nodes are built in order, the append function is suitable
        graph_neighbor.append(neighbors)
    return graph_neighbor

def get_node_score(graph_neighbors, graph_colors, node, node_score_list, attempt): # attempts to find how 'important' the node is
    if node_score_list[node] == 0:
        return 0 # node has been assigned permanently
    else:
        node_neighbors = graph_neighbors[node]
        node_score = len(node_neighbors) + len(graph_colors[node])
        for neighbor in node_neighbors:
            node_score += (len(graph_neighbors[neighbor]) - attempt*len(graph_colors[neighbor]))
        return max(node_score,1)

def assign_color(graph_neighbors, graph_colors, node, c_number):
    # we want to leave options open for other nodes. This is done by concatenating the arrays
    # of possible colors for all adjacent nodes and picking the least common color.
    # In case of a tie, choose the lowest color. Hopefully won't happen too often.
    colors = graph_colors[node]
    if len(colors) == 0: # no color available
        return -1
    else:
        color_distbn = []
        for neighbor in graph_neighbors[node]:
            color_distbn += graph_colors[neighbor]
        color_hist = []
        for color in colors:
            color_hist.append(color_distbn.count(color))
        return colors[color_hist.index(min(color_hist))]

def get_possible_colors(graph_neighbors, node, c_number, solution, node_score_list):
    colors = list(range(c_number)) # no duplicate colors
    for neighbor in graph_neighbors[node]:
        if solution[neighbor] in colors and node_score_list[neighbor] == 0:
            colors.remove(solution[neighbor])
    return colors


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

#   NEW CONSTRAINT PROGRAMMING METHOD
#   ===Description===
#   1. Sort nodes by how much they will constrain the search space once specified
#   2. Assign a color for that node that minimizes the loss of possible color for surrounding nodes
#   3. Re-sort and repeat until all nodes are assigned
#   ===RESULTS===
##    this got a 42/60 on the website which is sufficient.
##     Below is a list of nodes_edges for all 6 problems:
##     1. 50_350 (file 50_3)
##     2. 70_1678 (file 70_7)
##     3. 100_2502 (file 100_5)
##     4. 250_28046 (file 250_9)
##     5. 500_12565 (file 500_1)
##     6. 1000_249482 (file 1000_5)

    best_c_number = node_count
    # build a trivial solution
    # every node has its own color
    best_solution = range(0, node_count)
    graph_neighbors = build_graph_neighbors(node_count, edges)

    print("NODES: %d, EDGES: %d") % (node_count,len(edges))
    print("(ATTEMPT No., OBJ. VALUE)")
    for attempt in range(min(int(3001/node_count),50)): # will iterate at least 3 times
        c_number = 2 # lower bound for any graph where all nodes have at least 1 edge
        graph_colors = [] # lists possible colors for each unassigned node
        solution = [0]*node_count
        node_score_list = [1]*node_count
        for node in range(0,node_count): # gets initial colors
            possible_colors = get_possible_colors(graph_neighbors, node, c_number, solution, node_score_list)
            graph_colors.append(possible_colors)
        for node in range(0,node_count): # initial score
            node_score_list[node] = get_node_score(graph_neighbors, graph_colors, node, node_score_list, attempt)

        while any(node_score_list):
            high_node = node_score_list.index(max(node_score_list))
            assigned_color = assign_color(graph_neighbors, graph_colors, high_node, c_number)
            if assigned_color == -1:
                # no colors available; we have to increase the set of colors
                c_number += 1
                for node in range(0,node_count):
                    graph_colors[node] = get_possible_colors(graph_neighbors, node, c_number, solution, node_score_list)
                    node_score_list[node] = get_node_score(graph_neighbors, graph_colors, node, node_score_list, attempt)
            else:
                solution[high_node] = assigned_color
                node_score_list[high_node] = 0
                for neighbor in graph_neighbors[high_node]: # updates score and possible colors
                    graph_colors[neighbor] = get_possible_colors(graph_neighbors, neighbor, c_number, solution, node_score_list)
                    node_score_list[neighbor] = get_node_score(graph_neighbors, graph_colors, neighbor, node_score_list, attempt)

        print(attempt,c_number)
        if c_number < best_c_number:
            best_c_number = c_number
            best_solution = solution

    print("Best Solution Found (chromatic number, 0, and a vector of assigned colors):")
    color_count = best_c_number
    solution = best_solution

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

