# Python Server

The Python server’s main task is to define routes based on provided information.
This task entails 4 subtasks:
- retrieving data
- running an algorithm on the data
- building a url based on the algorithm’s results
- storing the urls and affiliated drivers and passengers in a matrix
- communicating said matrix to the PHP server

These subtasks are called in the main process: \__innit__

### \__innit__

Part of the main process is always running per while True loop.
In the above mentioned, the code checks what day it is and compares the current time with a deadline timetable
which was previously fetched from the DB's school table.
This deadline timetable consists of the different timezone differences
compared to UTC time. If the current time is within two minutes of one of the deadline times of the timetable,
a new thread will be started running the 4 subtasks consecutively.

    locations = one.select_all_addresses(i, day, y)
    vehicle_data, location_data, driver_indices, passenger_indices, drivers,\ passengers = one.locations(i, day, y)
    […]
    matrix = createDistanceMatrix.main(one.select_all_addresses(i, day, y))
    routes, dropped_nodes = Algorithm.main(vehicle_data, location_data, matrix)
    routes_temp = copy.deepcopy(routes)
    urls = construct_route_url(locations, routes_temp)
    […]
    temp1, temp2 = build_matrix(urls, routes, dropped_nodes, driver_indices, passenger_indices, drivers, passengers)
    filepath = fill_data_matrix(i, day, y, temp1, temp2)
    send_file(filepath)


### Retrieving data

Data is retrieved from the MySQL db using MySQL db connector in SQLHandler.py. Said class has multiple functions for
various data fetching tasks. But they all mostly follow the simple schema of:
        
    cursor = self.sql.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    # here result is a tuple of tuples 
    # the data of result is then manipulated 
    # to return the data in a desired fashion

### Algorithm	

The Algorithm requires the parameters vehicle_data, locations_data and distance_matrix.
With these values, a data model is created,
    
    def create_data_model(vehicle_data, location_data, distance_matrix):
    
which in turn is used to create a routing model,

    # Create the routing index manager.
	manager = pywrapcp.RoutingIndexManager(
	    len(data['distance_matrix']), data['num_vehicles'], data['starts'], data['ends'])

	# Create Routing Model.
	routing = pywrapcp.RoutingModel(manager)

to which several constraints are added, 

    # Define cost of each arc.
	routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
	[...]
	# Add Capacity constraint.
	[...]
	routing.AddDimensionWithVehicleCapacity(
		demand_callback_index,
		0,  # null capacity slack
		data['vehicle_capacities'],  # vehicle maximum capacities
		True,  # start cumul to zero
		'Capacity')
		
nodes are allowed to be dropped in case the demand is higher than the drivers can handle,

	# Allow to drop nodes.
	penalty = 100000000000
	# penalty must be larger than all distances of the distance_matrix added together minus the sum of the distances 
	# between the school(aka depot) and every node
	for node in range(1, len(data['distance_matrix'])):
		routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
	# note that no penalty is added to the depot(index=0)
	
search parameters are set

    # Setting first solution heuristic.
	search_parameters = pywrapcp.DefaultRoutingSearchParameters()
	search_parameters.first_solution_strategy = (
		routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

and finally the algorithm is run on the routing model using the aforementioned search parameters.
    
    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)
    
The return parameters are a list of list representing the routes and a list of dropped nodes.

    return routes, drop_nodes

### URL building

The URLs must follow the [url-encoding rules](https://developers.google.com/maps/documentation/urls/url-encoding),
i.e. must be properly escaped. This [guide](https://developers.google.com/maps/documentation/urls/guide) was used to
properly construct the url building module. First, a list is initiated, in order to be able to append it later on.
    
    urls = []

Then, the list of routes is looped through.

    if routes_temp != None:
		for i in routes_temp:
        [...]
    [...]

Before anything else, the beginning of the URL is set, because it is always the same.

    url = 'https://www.google.com/maps/dir/?api=1&origin='

Then, the first and the last locations each get a pointer, 

    x = i[0]
	z = i[len(i) - 1]
	
this start pointer is then used to set the origin value of the url.

    url += locations[x][0] + "+" + str(locations[x][1]) + "+" + locations[x][2] + "+" + locations[x][3] + "+" + locations[x][4] + "+" + locations[x][5]
    
It is then checked, if the current route has any waypoints in between origin and destination.

    if len(i) > 2:
        [...]

If true, then a waypoint string is appended to the url. 

    url += "&waypoints="

Also, start and end of the route are deleted from the route, so only a list of the route's waypoints is left.

    del i[0]
	del i[len(i) - 1]

Next, the waypoints are looped through.

    for y in i:
        url += locations[y][0] + "+" + str(locations[y][1]) + "+" + locations[y][2] + "+" + locations[y][3] + "+" + \
						   locations[y][4] + "+" + locations[y][5] + "%7C"

The last 3 characters are removed from the url string, else there would be one "%7C" to much.

    url = url[:-3]
    
The destination is added to  the url string.

    url += "&destination=" + locations[z][0] + "+" + str(locations[z][1]) + "+" + locations[z][2] + "+" + \
				   locations[z][3] + "+" + locations[z][4] + "+" + locations[z][5]

And finally the just build url is appended to the urls list and the urls list is returned at the very end.

            urls.append(url)
	return urls    
	
### Storing data in a matrix

The aforementioned urls need to be stored in an easily readable format,
so later on the php server has no problem distributing the data to the users.
This is achieved by using the .json format, which is easily readable for computers and humans.
The data of one algorithm run is stored in a one matrix file.

    {
    "type": "data_matrix",
    "day": "<day>",
    "school": "<school_id>",
    "timestamp": "<timestamp>",
    "data": [],
    "dropped_nodes": []
    }
    
The actual Matrix is the "data" array. This array is filled with driver objects.

    {
    "user_id": "<user_id>",
    "type": "driver",
    "url": "<url>",
    "passengers": []
    }

In these, the "passengers" array is then again filled with passenger objects.

    {
    "user_id": 0,
    "type": "",
    "user_id_driver": 0
    }

And in this way the data matrix provides the needed data in a usable, linked way.
