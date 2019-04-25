PythonServer-lifty
==================

A school project to reduce CO2-emissions by providing a platform to parents so they can take other children with them when 
driving their children to school.

Planned is a website, an Android app and a IOS app, also a python server,
which processes data and runs an algorithm on location 
data and the number of vehicles in order to find the optimal routes to the school.

This Project is being developed by the Q2 computer science course of the Königin-Luise-Stiftung Berlin school.

The provided code only represents the Python Server of the project.

In order to use the code:

  - create a database using the commands provided in SQL.sql
  - insert your database login data into json_config.json
  - insert your Google Distance Matrix API-Key into json_config.json
  - populate your database with userdata
  - in Json.py replace the "/PyhtonServer/..." filepaths with the actual filepaths of the according files.



# Structure of the program

The project consists of two main parts:

   - the frontend
   - the backend

The frontend is the interface between user and program, i. e. it is optimized for the aspects of usability and design. 

The backend is the heart of the program, i. e. it brings everything to life and must therefore be heavily tested on 
functionality and possible security risks.

# Structure of the frontend

The frontend is divided into three parts:
- browser interface(Website)
- Android interface(Java App)
- iOS interface(Swift App)

These three interfaces should follow relatively uniformly the given schema:

Registration:

The user has to register himself once in order to use the program.
In this process the user must enter personal data(forename, name, address),
contact data(tel, e-mail) and if they either are a parent(driver) or a child(passenger). The user also has to select a password.
Also a table of the child’s timetable should be entered, so the program knows who needs to be at the school at a certain time.

Login:

The user has to login every time they want to use the service, provided they are already registered.
In order to increase user-friendliness, an option for remembering login data should be made available.
	
Account management:

This pane is supposed to give the user the ability to change certain attributes of their account data.
Also an action for deleting the account should be provided.
		
Main page:

On this page an interface should be displayed, which gives the option for deciding if the user(driver) will be able to drive
the following day(yes/no) or if the user(passenger) wants to be picked up the next day(yes/no).
Additionally: Statistical data showing driven kilometers, number of rides, CO2 in t saved, polar bears saved etc.
Driver: A button needs to be displayed, which opens Google Maps with the route which needs to be driven. 
Passenger: A timecode needs to be displayed, which represents the time the passenger needs to be outside 
waiting to be picked up. Also the contact data of the driver needs to be displayed(tel).

# Structure of the backend 

The backend is divided into three different parts:
- PHP Server
- MySQL database(DB)
- Python Server
		
The PHP Server acts as a middle man between the user interface and the rest of the backend. 
That means, data is handed to the server, which communicates it to the DB.
Also, the Python Server hands data to the middle man, who distributes it then to the user interfaces. 
This practice is supposed to increase security while maintaining a minimal latency.

The MySQL database is the main structured data storing component of the program.
It stores data like user addresses, user logins etc. but also stores school data.
This DB is needed because a lot of data storing is required while it is also important,
that the data can be efficiently searched through.

The Python Server houses the algorithm, which produces the best routes for every driver,
every day, for every arrival time, for every school.
That is why it is so important to keep the server separate the rest of the backend,
it needs to be robust, secure and stable.
The Algorithm is called from a thread, which under certain conditions is started in the indefinitely running main process.

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
In the above mentioned, the code checks what day it is and compares the current time with a deadline timetable which was previously
fetched from the DB's school table. This deadline timetable consists of the different timezone differences compared to UTC time.
If the current time is within two minutes of one of the deadline times of the timetable,
a new thread will be started running the 4 subtasks consecutively.

<span style="color:blue">some *This is Blue italic.* text</span>


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
