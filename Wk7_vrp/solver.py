#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])

def length(c1, c2):
    return math.sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2)

def build_dist_from_depot(customers, depot):
    # only called once
    dist = []
    for c in customers:
        dist.append(round(length(c,depot),3))
    return dist

def get_dist_of_tour(depot,tour):
    # tour is passed as a list of customers not including the depot
    dist = 0
    if len(tour) > 0:
        dist += length(depot,tour[0])
        for i in range(0, len(tour)-1):
            dist += length(tour[i],tour[i+1])
        dist += length(tour[-1],depot)
    return dist

def get_next_c(remaining_customers, depot, cap_remaining):
    # this should return the 'apogee' or the farthest unassigned node from the depot
    # problem: some cases do not have any spare trucks. this means that a scenario can happen where no trucks can accomodate a large leftover item.
    # we can try a distance-demand product to fix this
    
    max_demand = max([c.demand for c in remaining_customers])
    if max_demand * 2 > max(cap_remaining):
        order = sorted(remaining_customers, key=lambda customer: -customer.demand)
        return order[0]
    
    cust = remaining_customers[0]
    max_score = 0
    for c in remaining_customers:
        score = c.demand * length(depot, c)
        if score > max_score:
            max_score = score
            cust = c
    return cust

def isvalid(customers, v_tours, v_capacity):
    # returns 1 if no vehicle is over capacity, 0 otherwise
    for tour in v_tours:
        if sum([c.demand for c in tour]) > v_capacity and sum([len(v) for v in v_tours]) == len(customers) - 1:
            return 0
    return 1

def loc_of_customer(v_tours, customer):
    # returns the vehicle and index of a customer, if it is assigned
    # returns -1 otherwise
    for vehicle, tour in enumerate(v_tours):
        for index, c in enumerate(tour):
            if c == customer:
                return vehicle, index
    return -1, -1


def get_obj_value(depot,vehicle_tours,vehicle_count):
    # whatever
    obj = 0
    for tour in vehicle_tours:
        obj += get_dist_of_tour(depot,tour)
    return obj

def print_full_tour_list(v_tours, depot):
    for tour in v_tours:
        tour_customers = [c.index for c in tour]
        tour_demand = sum([c.demand for c in tour])
        print(round(get_dist_of_tour(depot,tour),3), tour_demand, tour_customers)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])
    
    customers = []
    for i in range(1, customer_count+1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i-1, int(parts[0]), float(parts[1]), float(parts[2])))

    #the depot is always the first customer in the input
    depot = customers[0]
    print(f"Customers: {customer_count}, Vehicles: {vehicle_count}, Capacity: {vehicle_capacity}")
    max_demand = max([c.demand for c in customers])
    print(f"Largest Demand: {max_demand}")
    print(f"Depot: {depot.x}, {depot.y}")

    # build a trivial solution
    # assign customers to vehicles starting by the largest customer demands
    vehicle_tours = []
    
    remaining_customers = set(customers)
    remaining_customers.remove(depot)
    
    for v in range(0, vehicle_count):
        # print "Start Vehicle: ",v
        vehicle_tours.append([])
        cap_remaining = vehicle_capacity
        while sum([cap_remaining >= customer.demand for customer in remaining_customers]) > 0:
            used = set()
            order = sorted(remaining_customers, key=lambda customer: -customer.demand)
            for customer in order:
                if cap_remaining >= customer.demand:
                    cap_remaining -= customer.demand
                    vehicle_tours[v].append(customer)
                    # print '   add', ci, cap_remaining
                    used.add(customer)
            remaining_customers -= used

    # checks that the number of customers served is correct
    assert sum([len(v) for v in vehicle_tours]) == len(customers) - 1

# CP/LS Method
# We are trying to avoid using MIP because it's annoying
# Make a set of all 'apogee' tours, defined as a tour that reaches a node that is far from the depot and is full-cap. Each such tour will have a ratio of distance-per-customer (dpc).
# there are priorities for both distance and demand: a given full-cap tour could be close to the depot and loop in a wide area, or far from the depot in a narrow area. We prefer the latter, in order to avoid paths which cross over each other.
# in order of dist from depot, add nodes to the given tour that adds the least amount of distance, i.e., either to an existing v or to a new v (similar to facility location).

# RESULTS:
# (problem) result value > best value
# 1. (16_3) 324 > 280
# 2. (26_8) 731 > 630
# 3. (51_5) 577 > 540
# 4. (101_10) 1135 > 830
# 5. (200_16) 1881 > 1400
# 6. (421_41) 2236 > 2000

    v_tours_ls = [ [] for i in range(vehicle_count)]
    remaining_customers = list(customers)
    remaining_customers.remove(depot)
    cap_remaining = [vehicle_capacity]*vehicle_count
    dist_from_depot = build_dist_from_depot(customers, depot)

    while len(remaining_customers) > 0:
        c = get_next_c(remaining_customers, depot, cap_remaining)
        # this currently returns the highest-demand customer
        # we can also try adding a check to the above so that if there is one-and-only-one v that fits the maximum c, then return that c, and otherwise go with a more optimal c
        best_dist = float('inf')
        best_v = cap_remaining.index(max(cap_remaining))
        # defaults to the vehicle with the most room left
        best_i = 0
        # try all possible assignments and go with the one that adds the least distance
        for vehicle, tour in enumerate(v_tours_ls):
            if cap_remaining[vehicle] >= c.demand:
                test_tour = list(tour)
                for i in range(len(test_tour) + 1):
                    test_tour.insert(i,c)
                    test_dist = get_dist_of_tour(depot, test_tour)
                    if test_dist < best_dist:
                        best_v = vehicle
                        best_i = i
                        best_dist = test_dist
                    test_tour.remove(c)
        remaining_customers.remove(c)
        v_tours_ls[best_v].insert(best_i,c)
        cap_remaining[best_v] -= c.demand
    
    print("Initial Solution:")
    print_full_tour_list(v_tours_ls, depot)
    obj = get_obj_value(depot, v_tours_ls, vehicle_count)
    print("Capacities Remaining:")
    print(cap_remaining)


    print("Starting Local Search...")
    # TO DO: Add LS
    # method:
    # for each v:
    #   for each c in v:
    #       test_case = that c swapped with every other node in the set
    #       if test_case < best_case and capacities are valid:
    #           keep the solution
    # the number of swaps should be roughly quadratic, or about 180K for the largest case
    # since each customer is guaranteed assigned, we can access and swap them in order, even though they are almost certainly out of order in the solution

    current_best_obj = obj
    attempt = 0
    while True:
        attempt += 1
        print(f"Attempt: {attempt}")
        print(f"Current Best Obj. Value: {current_best_obj}")
        no_improvement = True
        for i in range(1,len(customers)-1):
            for k in range(i+1,len(customers)):
                test_v_tours = []
                for tour in v_tours_ls:
                    test_v_tours.append(list(tour))
                
                c1 = customers[i]
                c2 = customers[k]
                c1v, c1i = loc_of_customer(test_v_tours, c1)
                c2v, c2i = loc_of_customer(test_v_tours, c2)
                test_v_tours[c1v][c1i] = c2
                test_v_tours[c2v][c2i] = c1
                test_obj = get_obj_value(depot, test_v_tours, vehicle_count)
                
                if test_obj < current_best_obj and isvalid(customers, test_v_tours, vehicle_capacity):
                    v_tours_ls = list(test_v_tours)
                    current_best_obj = test_obj
                    no_improvement = False
        if no_improvement:
            break

    print("Local Search Finished.")
    print(f"Obj. Value before Local Search: {round(obj, 2)}")
    print(f"Obj. Value after Local Search: {round(current_best_obj, 2)}")
    if isvalid(customers, v_tours_ls, vehicle_capacity):
        print("Solution Found:")
    

    # calculate the cost of the solution; for each vehicle the length of the route
    vehicle_tours = v_tours_ls
    obj = get_obj_value(depot,vehicle_tours,vehicle_count)

    # prepare the solution in the specified output format
    outputData = '%.2f' % obj + ' ' + str(0) + '\n'
    for v in range(0, vehicle_count):
        outputData += str(depot.index) + ' ' + ' '.join([str(customer.index) for customer in vehicle_tours[v]]) + ' ' + str(depot.index) + '\n'

    return outputData


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:

        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')

