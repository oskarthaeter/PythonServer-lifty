import copy
from datetime import datetime, time, date

import threading

from src import Algorithm, createDistanceMatrix
from src.Json import fill_data_matrix, build_list
from src.SQLHandler import SQLHandler
from src.url_constructer import construct_route_url

one = SQLHandler()


def is_time_between(begin_time, end_time, check_time=None):
	# If check time is not given, default to current time
	check_time = check_time or datetime.now().time()
	if begin_time < end_time:
		return check_time >= begin_time and check_time <= end_time
	else:  # crosses midnight
		return check_time >= begin_time or check_time <= end_time


# parameters: day, schools
# format:     str, list(int)
def run_thread(day, schools):
	for i in schools:
		group = one.build_time_pool(day, i)
		for y in group:
			locations = one.select_all_addresses(i, day, y)
			vehicle_data, location_data, driver_indices, passenger_indices, drivers, passengers = one.locations(i, day, y)
			# potential bug when requests to google distance matrix api are synchronized (DDoS attack)
			# https://developers.google.com/maps/documentation/distance-matrix/web-service-best-practices#synchronized-requests
			matrix = createDistanceMatrix.main(one.select_all_addresses(i, day, y))
			routes, dropped_nodes = Algorithm.main(vehicle_data, location_data, matrix)
			routes_temp = copy.deepcopy(routes)
			urls = construct_route_url(locations, routes_temp)
			for u in urls:
				print(u)
			temp1, temp2 = build_matrix(urls, routes, dropped_nodes, driver_indices, passenger_indices, drivers, passengers)
			filepath, filename = fill_data_matrix(i, day, y, temp1, temp2)
			ftp_upload(filepath, filename)


def add_timezone(time, timezone):
	sum = time + timezone
	if sum >= 24:
		sum = sum - 24
	elif sum < 0:
		sum = 24 + sum
	output_hours = (sum - (sum % 100)) / 100
	output_minutes = sum % 100
	if output_minutes >= 60:
		output_minutes -= 60
		output_hours += 1
	if output_hours >= 24:
		output_hours -= 24
	return int(output_hours), int(output_minutes)


def main():
	days = {}
	days['Sunday'] = 'monday'
	days['Monday'] = 'tuesday'
	days['Tuesday'] = 'wednesday'
	days['Wednesday'] = 'thursday'
	days['Thursday'] = 'friday'
	days['Friday'] = None
	days['Saturday'] = None

	while True:
		one = SQLHandler()
		threads = []
		timezones = one.build_timezone_pool()
		already_run = False
		print("here")
		for t in timezones:
			hours, minutes = add_timezone(2000, t)
			if days[date.today().strftime("%A")] is not None and is_time_between(time(hours, minutes), time(hours, minutes + 2)) and already_run is False:
				day = days[date.today().strftime("%A")]
				schools = one.build_school_pool(t)
				thread = threading.Thread(target=run_thread, args=(day, schools))
				thread.start()
				threads.append(thread)
				already_run = True


if __name__ == '__main__':
	main()
