#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def find_closest_not_assigned(points, unassigned, last_point): # finds the closest unassigned node to the last node in the solution
    
    close_node = unassigned[0]
    close_diff_x = abs(last_point.x - points[close_node].x)
    close_diff_y = abs(last_point.y - points[close_node].y)
    min_distance = length(last_point, points[close_node])
    
    for i in unassigned:
        if abs(points[i].x - last_point.x) < close_diff_x or abs(points[i].y - last_point.y) < close_diff_y:
            distance = length(last_point, points[i])
            if distance < min_distance:
                close_node = i
                min_distance = distance
                close_diff_x = abs(last_point.x - points[i].x)
                close_diff_y = abs(last_point.y - points[i].y)

    return close_node

def get_total_length(points, path):
    if len(path) < 2:
        return 0
    else:
        total_length = length(points[path[-1]], points[path[0]])
    if len(path) > 2:
        for index in range(0, len(path)-1):
            total_length += length(points[path[index]], points[path[index+1]])
    return total_length

def is_better(points, best, contender):
    # returns 1 if the contender solution is better than the best solution, 0 otherwise
    while best[0] == contender[0] and len(best) > 1:
        best = best[1:]
        contender = contender[1:]
    while best[-1] == contender[-1] and len(best) > 1:
        best = best[:-1]
        contender = contender[:-1]

    best_total_length = get_total_length(points, best)
    contender_total_length = get_total_length(points, contender)
    if contender_total_length < best_total_length: # lower is better
        return 1
    else:
        return 0

def opt2(points, solution):
    # tries all swaps on the solution
    # not guaranteed to get the global optimum with a single call
    best_total_length = get_total_length(points, solution)
    for i in range(len(solution)-1):
        if length(points[solution[i]],points[solution[i+1]]) < best_total_length/(len(solution)*2):
            # arbitrary but helps skip over edges that are already very short
            pass
        else:
            for k in range(i+1,len(solution)):
                swap = solution[i:k]
                swap.reverse()
                test_solution = solution[:i] + swap + solution[k:]
                test_total_length = get_total_length(points, test_solution)
                if test_total_length < best_total_length:
                    if len(solution) >= 574:
                        print(i, best_total_length, test_total_length - best_total_length)
                    best_total_length = test_total_length
                    solution = list(test_solution)
    return solution


def get_greedy_from_seedy(points, seed):
    unassigned = list(set(range(len(points))) - set(seed))
    while len(seed) < len(points):
        last_point = points[seed[-1]]
        next_point = find_closest_not_assigned(points, unassigned, last_point)
        seed.append(next_point)
        unassigned.remove(next_point)
    return seed

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))
    
    x_avg = y_avg = 0
    for point in points:
        x_avg += point.x/nodeCount
        y_avg += point.y/nodeCount

    avg_point = Point(x_avg, y_avg)

    # greedy + 2-opt results (low quality, high quality):
    # 448 (482, 430), 23097 (23433, 20800), 32723 (35985, 30000), 39704 (40000, 37600), 361K (378K, 323K), 78.4M (78.5M, 67.7M)

    print("Points: %d") % (nodeCount)
    print("Average Point: %f, %f") % (x_avg, y_avg)

    solution = list(range(0,nodeCount)) # trivial; this is actually the best for tc_574_1
    best_total_length = get_total_length(points, solution)
    print("Default: %f") % (best_total_length)
    step = 1
    threshold = 574 # number of nodes to be considered 'large'
    max_nodes = 33810 # only the 30K dataset is this big
    if nodeCount >= threshold:
        step = 5
    if nodeCount >= max_nodes:
        step = 10000

    print("Step: %d") % (step)
    for seed in range(0,nodeCount,step):
        if nodeCount >= max_nodes:
            print("Starting seed: %d") % (seed)
        solution_seed = get_greedy_from_seedy(points, [seed])
        if nodeCount < threshold:
            solution_seed = opt2(points, solution_seed)
        test_length = get_total_length(points, solution_seed)
        print("Seed %d: %f") % (seed, test_length)
        if test_length < best_total_length:
            solution = list(solution_seed)
            best_total_length = test_length
            print("NEW BEST")

    print("Best Path Length from greedy: %f") % (best_total_length)


    for i in range(0,threshold,int(nodeCount/2)):
        print("Starting 2-opt again...")
        solution = opt2(points, solution)

    # calculate the length of the tour
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, nodeCount-1):
        obj += length(points[solution[index]], points[solution[index+1]])

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

