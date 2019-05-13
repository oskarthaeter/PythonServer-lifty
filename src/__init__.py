import copy
import datetime

import threading
from time import sleep

from Communication import sftp_upload
from Time import add_timezone, time_in_range
from src import Algorithm, createDistanceMatrix
from src.Json import fill_data_matrix, build_list
from src.SQLHandler import SQLHandler
from src.url_constructer import construct_route_url

one = SQLHandler()


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
			matrix, time_matrix = createDistanceMatrix.main(one.select_all_addresses(i, day, y))
			routes, dropped_nodes, durations = Algorithm.main(vehicle_data, location_data, matrix, time_matrix)
			routes_temp = copy.deepcopy(routes)
			urls = construct_route_url(locations, routes_temp)
			for u in urls:
				print(u)
			temp1, temp2 = build_list(urls, routes, dropped_nodes, driver_indices, passenger_indices, drivers, passengers, day, y, durations)
			filepath, filename = fill_data_matrix(i, day, y, temp1, temp2)
			sftp_upload(filepath, filename)
	sleep(120)


def main():
	days = {}
	days['Sunday'] = 'monday'
	days['Monday'] = 'tuesday'
	days['Tuesday'] = 'wednesday'
	days['Wednesday'] = 'thursday'
	days['Thursday'] = 'friday'
	days['Friday'] = None
	days['Saturday'] = None

	deadline = datetime.time(20, 0, 0)

	while True:
		one = SQLHandler()
		threads = []
		timezones = one.build_timezone_pool()
		already_run = False
		print("here")
		for t in timezones:
			print(t)
			time_in_timezone = add_timezone(deadline, t)
			if days[datetime.date.today().strftime("%A")] is not None and time_in_range(deadline, datetime.time(20, 2, 0), time_in_timezone) and already_run is False:
				day = days[datetime.date.today().strftime("%A")]
				schools = one.build_school_pool(t)
				thread = threading.Thread(target=run_thread, args=(day, schools))
				thread.start()
				threads.append(thread)
				already_run = True


if __name__ == '__main__':
	main()
