#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
import numpy as np

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def build_distance_table(facilities, customers):
    # distance from f's to c's; only called once
    distance_table = np.zeros((len(facilities), len(customers)))
    for facility in facilities:
        for customer in customers:
            distance_table[facility.index, customer.index] = length(facility.location, customer.location)
    return distance_table

def find_avg_point(customers):
    # only called once
    x_avg = y_avg = 0
    for customer in customers:
        x_avg += customer.location.x/len(customers)
        y_avg += customer.location.y/len(customers)
    return Point(round(x_avg,2), round(y_avg,2))

def get_obj_value(distance_table, facilities, customers, solution, f_assigned):
    # gets the cost of a single f and any indicated c's
    obj = 0
    for f in facilities:
        obj += f_assigned[f.index] * facilities[f.index].setup_cost
    for index, assigned_c in enumerate(solution):
        obj += distance_table[assigned_c, index]
    return obj

def get_cost_of_setup(facility, c_set):
    # gets the cost of a single f and any indicated c's
    cost = facility.setup_cost
    for customer in c_set:
        cost += length(customer.location, facility.location)
    return cost


def get_low_cost_set(distance_table, facility, customers, solution):
    # finds closest available c's to a f until capacity is reached
    # may try an inverse; for each c in order of demand, assign it to the nearest f.
    
    cap = facility.capacity
    # c_copy = list(customers)
    c_distances = distance_table[facility.index].tolist()
    c_demands = [c.demand for c in customers]
    low_cost_set = []
    # find the lowest-distance customer and pop it
    # if it is unassigned and cap > demand: add it to open_set and update cap
    while len(c_distances) > 0:
        c_close_index = c_distances.index(min(c_distances)) # c_distances
        c_distances.pop(c_close_index)
        c_closest = customers.pop(c_close_index)
        if solution.pop(c_close_index) == -1 and c_closest.demand <= cap:
            low_cost_set.append(c_closest)
            cap -= c_closest.demand
        if cap < min(c_demands): # speedup
            break
    return low_cost_set

def find_unassigned_point(customers, solution, avg_point):
    # try to ensure compactness of the solution by prioritizing points that are near the average of all assigned points
    # we could also try finding the free-point closest to just the most recently assigned facility
    # we could also try finding the free-point farthest from the average of all points
    # not modifying original lists here
    dist = float("inf")
    for customer in customers:
        if solution[customer.index] == -1 and length(customer.location, avg_point) < dist:
            dist = length(customer.location, avg_point)
            c_unassigned = customer
    return c_unassigned

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

# Number of f's, c's (filename) and the first-pass values (threshold values):
# 25, 50:               3.82M (4M, 3.26M)
# 50, 200 (50_6):       5.421M (4.5M, ?)
# 100, 100:             1965 (2050) (Full marks)
# 100, 1000 (100_1):    26.5M (26M, ?)
# 200, 800 (200_7):     5.81M (5M, ?)
# 500, 3000 (500_7):    31.6M (30M, ?)
# 1000, 1500 (1000_2):  10.41M (10M, ?)
# 2000, 2000:           7.9M (10M, 7.45M)

# ideas:
# assign f's accroding to their relative spacing, rather than just going with the lowest-cost f every time. Make sure that the next f to be assigned includes the unassigned point closest to the average of all assigned f's.

    

    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]
    avg_point = find_avg_point(customers)

    print(f"Facilities: {len(facilities)}, Customers: {len(customers)}")
    print(f"Average Point: {avg_point}")
    print("Building Distance Table...")

    distance_table = build_distance_table(facilities,customers)
    f_cpc = [f.setup_cost for f in facilities]
    f_lcs = [0]*len(facilities)
    f_assigned = [0]*len(facilities)
    obj = 0

    print("Finding Efficient Locations...")
    print("Facility, Cap Used, Cap Left, Setup Cost, Total Cost, CPC, Low Cost Set")

    while(min(solution) == -1):
        for facility in facilities:
            if not any(f_assigned) or (not f_assigned[facility.index] and max([solution[c.index] for c in f_lcs[facility.index]]) > -1):
                # condition should only evaluate f's whose sets were affected by the previous assignment
                low_cost_set = get_low_cost_set(distance_table, facility, list(customers), list(solution))
                cost_of_setup = get_cost_of_setup(facility, low_cost_set) - 0 * facility.setup_cost
                f_cpc[facility.index] = cost_of_setup/max(len(low_cost_set),1)
                f_lcs[facility.index] = low_cost_set
            # we can try either assigning the lowest-cost f, or assigning the f with the lowest cost-per-customer
        f_lowest_cpc_found = float("inf")
        f_low = f_assigned.index(0) # there will always be at least one f unassigned
        c_unassigned = find_unassigned_point(customers, solution, avg_point)
        for facility in facilities:
            if not f_assigned[facility.index] and f_cpc[facility.index] < f_lowest_cpc_found:
                f_low = facility.index
                f_lowest_cpc_found = f_cpc[facility.index]

        cap_used = sum([c.demand for c in f_lcs[f_low]])
        cap = facilities[f_low].capacity
        print(f_low, cap_used, cap-cap_used, facilities[f_low].setup_cost, round(f_cpc[f_low]*len(f_lcs[f_low]),2), round(f_cpc[f_low],2), [f.index for f in f_lcs[f_low]])

        obj += get_cost_of_setup(facilities[f_low], f_lcs[f_low])
        for c in f_lcs[f_low]:
            solution[c.index] = f_low
        f_assigned[f_low] = 1

    obj2 = get_obj_value(distance_table, facilities, customers, solution, f_assigned)
    print(f"Total Facilities Assigned: {sum(f_assigned)} of {len(facilities)}")
    print(f"Average Cost per Facility: {round(obj/sum(f_assigned),2)}")
    print(f"Average Cost per Customer: {round(obj/len(customers),2)}")

    # trivial solution
#    facility_index = 0
#    for customer in customers:
#        if capacity_remaining[facility_index] >= customer.demand:
#            solution[customer.index] = facility_index
#            capacity_remaining[facility_index] -= customer.demand
#        else:
#            facility_index += 1
#            assert capacity_remaining[facility_index] >= customer.demand
#            solution[customer.index] = facility_index
#            capacity_remaining[facility_index] -= customer.demand
#
#    used = [0]*len(facilities)
#    for facility_index in solution:
#        used[facility_index] = 1
#
#
#    # calculate the cost of the solution
#    obj = sum([f.setup_cost*used[f.index] for f in facilities])
#    for customer in customers:
#        obj += length(customer.location, facilities[solution[customer.index]].location)

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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

