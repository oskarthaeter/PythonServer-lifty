"""Capacitated Vehicle Routing Problem (CVRP).
   This is a sample using the routing library python wrapper to solve a CVRP
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.
   Distances are in meters.
"""

from __future__ import print_function
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def create_data_model(vehicle_data, location_data, distance_matrix):
	"""Stores the data for the problem"""
	data = {}

	data['distance_matrix'] = distance_matrix
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
	print(dropped_nodes)
	# Display routes
	total_distance = 0
	total_load = 0
	routes = []
	for vehicle_id in range(data['num_vehicles']):
		route = []
		index = routing.Start(vehicle_id)
		plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
		route_distance = 0
		route_load = 0
		while not routing.IsEnd(index):
			node_index = manager.IndexToNode(index)
			route_load += data['demands'][node_index]
			plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
			route.append(manager.IndexToNode(index))
			previous_index = index
			index = assignment.Value(routing.NextVar(index))
			route_distance += routing.GetArcCostForVehicle(
				previous_index, index, vehicle_id)
		plan_output += ' {0} Load({1})\n'.format(
			manager.IndexToNode(index), route_load)
		route.append(manager.IndexToNode(index))
		plan_output += 'Distance of the route: {}m\n'.format(route_distance)
		plan_output += 'Load of the route: {}\n'.format(route_load)
		print(plan_output)
		total_distance += route_distance
		total_load += route_load
		routes.append(route)
	print('Total Distance of all routes: {}m'.format(total_distance))
	print('Total Load of all routes: {}'.format(total_load))
	print(routes)
	return routes, drop_nodes


def main(vehicle_data, location_data, distance_matrix):
	# Instantiate the data problem.
	data = create_data_model(vehicle_data, location_data, distance_matrix)

	# Create the routing index manager.
	manager = pywrapcp.RoutingIndexManager(
		len(data['distance_matrix']), data['num_vehicles'], data['starts'], data['ends'])

	# Create Routing Model.
	routing = pywrapcp.RoutingModel(manager)

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
	penalty = 10000000
	for node in range(1, len(data['distance_matrix'])):
		routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

	# Setting first solution heuristic.
	search_parameters = pywrapcp.DefaultRoutingSearchParameters()
	search_parameters.first_solution_strategy = (
		routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

	# Solve the problem.
	assignment = routing.SolveWithParameters(search_parameters)

	# Print solution on console.
	if assignment:
		return print_solution(data, manager, routing, assignment)