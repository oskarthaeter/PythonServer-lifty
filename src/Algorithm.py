#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Capacitated Vehicle Routing Problem (CVRP).
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.
   Distances are in meters.
"""

import __future__
import logging

import ortools.constraint_solver.pywrapcp
import ortools.constraint_solver.routing_enums_pb2

logger_2 = logging.getLogger('PythonServer.Algorithm')

def create_data_model(vehicle_data, location_data, distance_matrix, time_matrix):
	"""Stores the data for the problem"""
	data = {}

	data['distance_matrix'] = distance_matrix
	data['time_matrix'] = time_matrix
	data['demands'] = [0]
	for i in range(1, (location_data['num'])):
		data['demands'].append(1)
	data['vehicle_capacities'] = vehicle_data['capacities']
	data['num_vehicles'] = vehicle_data['num']
	data['num_locations'] = location_data['num']
	data['starts'] = location_data['starts']
	data['ends'] = []
	for i in range(0, (vehicle_data['num'])):
		data['ends'].append(0)
	return data


def print_solution(data, manager, routing, assignment):
	"""Prints assignment on console."""
	# Display dropped nodes.
	dropped_nodes = 'Dropped nodes:'
	drop_nodes = []
	for node in range(routing.Size()):
		if routing.IsStart(node) or routing.IsEnd(node):
			continue
		if assignment.Value(routing.NextVar(node)) == node:
			dropped_nodes += ' {}'.format(manager.IndexToNode(node))
			drop_nodes.append(manager.IndexToNode(node))
	logger_2.info(dropped_nodes)
	# Display routes
	total_distance = 0
	total_duration = 0
	total_load = 0
	routes = []
	durations = []
	for vehicle_id in range(data['num_vehicles']):
		route = []
		duration = []
		index = routing.Start(vehicle_id)
		plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
		route_distance = 0
		route_duration = 0
		route_load = 0
		while not routing.IsEnd(index):
			node_index = manager.IndexToNode(index)
			route_load += data['demands'][node_index]
			plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
			route.append(manager.IndexToNode(index))
			previous_index = index
			index = assignment.Value(routing.NextVar(index))
			route_duration += data['time_matrix'][manager.IndexToNode(previous_index)][manager.IndexToNode(index)]
			duration.append(route_duration)
			route_distance += routing.GetArcCostForVehicle(
				previous_index, index, vehicle_id)
		plan_output += ' {0} Load({1})\n'.format(
			manager.IndexToNode(index), route_load)
		route.append(manager.IndexToNode(index))
		if route_distance == 0:
			route_distance = data['distance_matrix'][manager.IndexToNode(routing.Start(vehicle_id))][0]
		plan_output += 'Distance of the route: {}m\n'.format(route_distance)
		plan_output += 'Load of the route: {}\n'.format(route_load)
		plan_output += 'Duration of the route: {}\n'.format(duration)
		plan_output += 'Total duration of the route: {}min \n'.format(route_duration / 60)
		logger_2.info(plan_output)
		total_distance += route_distance
		total_duration += route_duration
		total_load += route_load
		routes.append(route)
		durations.append(duration)
	logger_2.info('Total Distance of all routes: {}m'.format(total_distance))
	logger_2.info('Total Duration of all routes: {}min'.format(total_duration/60))
	logger_2.info('Total Load of all routes: {}'.format(total_load))
	logger_2.info(routes)
	logger_2.info(durations)
	return routes, drop_nodes, durations


def main(vehicle_data, location_data, distance_matrix, time_matrix):
	# Instantiate the data problem.
	data = create_data_model(vehicle_data, location_data, distance_matrix, time_matrix)

	# Create the routing index manager.
	manager = ortools.constraint_solver.pywrapcp.RoutingIndexManager(
		len(data['distance_matrix']), data['num_vehicles'], data['starts'], data['ends'])

	# Create Routing Model.
	routing = ortools.constraint_solver.pywrapcp.RoutingModel(manager)

	# Create and register a transit callback.
	def distance_callback(from_index, to_index):
		"""Returns the distance between the two nodes."""
		# Convert from routing variable Index to distance matrix NodeIndex.
		from_node = manager.IndexToNode(from_index)
		to_node = manager.IndexToNode(to_index)
		return data['distance_matrix'][from_node][to_node]

	transit_callback_index = routing.RegisterTransitCallback(distance_callback)

	# Define cost of each arc.
	routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

	# Add Capacity constraint.
	def demand_callback(from_index):
		"""Returns the demand of the node."""
		# Convert from routing variable Index to demands NodeIndex.
		from_node = manager.IndexToNode(from_index)
		return data['demands'][from_node]

	demand_callback_index = routing.RegisterUnaryTransitCallback(
		demand_callback)
	routing.AddDimensionWithVehicleCapacity(
		demand_callback_index,
		0,  # null capacity slack
		data['vehicle_capacities'],  # vehicle maximum capacities
		True,  # start cumul to zero
		'Capacity')
	# Allow to drop nodes.
	penalty = 100000000000
	# penalty must be larger than all distances of the distance_matrix added together minus the sum of the distances
	# between the school(aka depot) and every node
	for node in range(1, len(data['distance_matrix'])):
		routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
	# note that no penalty is added to the depot(index=0)

	# Setting first solution heuristic.
	search_parameters = ortools.constraint_solver.pywrapcp.DefaultRoutingSearchParameters()
	search_parameters.first_solution_strategy = (
		ortools.constraint_solver.routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

	# Solve the problem.
	assignment = routing.SolveWithParameters(search_parameters)

	# Print solution on console.
	if assignment:
		return print_solution(data, manager, routing, assignment)
