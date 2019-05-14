import json

# handles json data

# loads a json file and returns a data dict
import Time


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


def get_config_sftp():
	data = load_json("/PythonServer/files/json/json_config.json")
	return data["sftp-server"]["host"], data["sftp-server"]["username"], data["sftp-server"]["password"]


# fills the driver json file and returns a data dict
def fill_driver_data(user_id, url, duration, time):
	data = load_json("/Users/oskarhaeter/PycharmProjects/PythonServer/files/json/json_form_driver_data.json")
	data["user_id"] = user_id
	data["url"] = url
	data["duration"] = duration
	data["pick_up"] = Time.new_time_string_for_time(Time.subtract_time(Time.datetime_for_time(time), duration+300).time())
	return data


# fills the passenger json file and returns a data dict
def fill_passenger_data(user_id, day, time, driver_id, duration, total_duration):
	import SQLHandler
	one = SQLHandler.SQLHandler()
	data = load_json("/Users/oskarhaeter/PycharmProjects/PythonServer/files/json/json_form_passenger_data.json")
	data["user_id"] = user_id
	forename, name = one.driver_name(driver_id)
	data["url"] = "You're to be picked up on {} to arrive before {} at your school from {} {}. ".format(day, Time.new_time_string_for_time(time), forename, name)
	data["url"] += "You will be picked up at around {}".format(Time.new_time_string_for_time(Time.subtract_time(Time.datetime_for_time(time), ((total_duration + 300) - duration)).time()))
	data["duration"] = duration
	data["pick_up"] = Time.new_time_string_for_time(Time.subtract_time(Time.datetime_for_time(time), ((total_duration + 300) - duration)).time())
	return data


def fill_dropped_data(user_id):
	data = load_json("/PythonServer/files/json/json_form_passenger_data.json")
	data["user_id"] = user_id
	data["url"] = "Unfortunately we could not find anybody to pick you up."
	return data


# fills the data matrix json file, saves it and returns the path of the just created file
def fill_data_matrix(school_id, day, timestamp, fill_data, dropped_nodes):
	data = load_json("/PythonServer/files/json/json_form_data_matrix.json")
	data["type"] = "data_matrix"
	data["day"] = day
	data["school"] = school_id
	data["timestamp"] = Time.new_time_string_for_time(timestamp)
	data["data"] = fill_data
	data["dropped_nodes"] = dropped_nodes
	print(data)
	with open('/Users/oskarhaeter/PycharmProjects/PythonServer/files/output/data_{}_{}_{}.json'.format(school_id, day, Time.new_time_string_for_time(timestamp)), 'w', encoding='utf8') as outfile:
		json.dump(data, outfile, ensure_ascii=False)
	return '/Users/oskarhaeter/PycharmProjects/PythonServer/files/output/data_{}_{}_{}.json'.format(school_id, day, Time.new_time_string_for_time(timestamp)), 'data_{}_{}_{}.json'.format(school_id, day, Time.new_time_string_for_time(timestamp))


def build_list(urls, routes, dropped_nodes, drivers, passengers, driver_indices, passenger_indices, day, time, durations):
	driver_list = []
	passenger_list = []
	for r in routes:
		pointer = routes.index(r)
		index = drivers.index(int(r[0]))
		start = driver_indices[index]
		del r[0]
		del r[len(r) - 1]
		for o in r:
			passenger_pointer = r.index(o)
			passenger_list.append(fill_passenger_data(passenger_indices[passengers.index(o)], day, time, start, durations[pointer][passenger_pointer], durations[pointer][len(durations[pointer])-1]))
		driver_list.append(fill_driver_data(start, urls[pointer], durations[pointer][len(durations[pointer])-1], time))
	output_dropped_nodes = []
	for d in dropped_nodes:
		output_dropped_nodes.append(fill_dropped_data(passenger_indices[passengers.index(d)]))
	list = driver_list + passenger_list
	return list, output_dropped_nodes