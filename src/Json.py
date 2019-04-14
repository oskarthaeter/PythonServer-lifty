import json


# handles json data

# loads a json file and returns a data dict
def load_json(file_name):
	with open(file_name, "r") as read_file:
		data = json.load(read_file)
	return data


# gets the login data for the mysql db from the json config file
def get_config_db():
	data = load_json("/PythonServer/files/json/json_config.json")
	return data["db"]["user"], data["db"]["password"], data["db"]["host"], data["db"]["database"]


# gets the api key for the google distance matrix api from the config json file
def get_config_api_key():
	data = load_json("/PythonServer/files/json/json_config.json")
	return data["google"]["API_KEY"]


# fills the driver json file and returns a data dict
def fill_driver_data(user_id, url, passengers):
	data = load_json("/PythonServer/files/json/json_form_driver_data.json")
	data["user_id"] = user_id
	data["type"] = "driver"
	data["url"] = url
	data["passengers"] = passengers
	return data


# fills the passenger json file and returns a data dict
def fill_passenger_data(user_id, driver_id):
	data = load_json("/PythonServer/files/json/json_form_passenger_data.json")
	data["user_id"] = user_id
	data["type"] = "passenger"
	data["user_id_driver"] = driver_id
	return data


# fills the data matrix json file, saves it and returns the path of the just created file
def fill_data_matrix(school_id, day, timestamp, fill_data, dropped_nodes):
	data = load_json("/PythonServer/files/json/json_form_data_matrix.json")
	data["type"] = "data_matrix"
	data["day"] = day
	data["school"] = school_id
	data["timestamp"] = timestamp
	data["data"] = fill_data
	data["dropped_nodes"] = dropped_nodes
	print(data)
	with open('/PythonServer/files/json/data_{}_{}_{}.json'.format(school_id, day, timestamp), 'w', encoding='utf8') as outfile:
		json.dump(data, outfile, ensure_ascii=False)
	return '/PythonServer/files/json/data_{}_{}_{}.json'.format(school_id, day, timestamp)


# builds the actual matrix which has the following structure:
# data->drivers->passengers
# dropped_nodes->passengers
def build_matrix(urls, routes, dropped_nodes, drivers, passengers, driver_indices, passenger_indices):
	matrix = []
	for r in routes:
		pointer = routes.index(r)
		index = drivers.index(int(r[0]))
		start = driver_indices[index]
		passenger_pool = []
		del r[0]
		del r[len(r) - 1]
		for o in r:
			passenger_pool.append(fill_passenger_data(passenger_indices[passengers.index(o)], start))
		matrix.append(fill_driver_data(start, urls[pointer], passenger_pool))
	output_dropped_nodes = []
	print(dropped_nodes)
	for d in dropped_nodes:
		output_dropped_nodes.append(passenger_indices[passengers.index(d)])
	return matrix, output_dropped_nodes
