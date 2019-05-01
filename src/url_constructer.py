# class for building a url linking to a google maps route
import copy

from Communication import sftp_upload
from src import Algorithm, createDistanceMatrix
from src.Json import build_list, fill_data_matrix
from src.SQLHandler import SQLHandler


# urls constructed in accordance with:
# https://developers.google.com/maps/documentation/urls/guide
# https://developers.google.com/maps/documentation/urls/url-encoding
def construct_route_url(locations, routes_temp):
	urls = []
	if routes_temp != None:
		for i in routes_temp:
			url = 'https://www.google.com/maps/dir/?api=1&origin='
			x = i[0]
			z = i[len(i) - 1]
			url += locations[x][0] + "+" + str(locations[x][1]) + "+" + locations[x][2] + "+" + locations[x][3] + "+" + \
				   locations[x][4] + "+" + locations[x][5]
			if len(i) > 2:
				url += "&waypoints="
				del i[0]
				del i[len(i) - 1]
				for y in i:
					url += locations[y][0] + "+" + str(locations[y][1]) + "+" + locations[y][2] + "+" + locations[y][
						3] + "+" + \
						   locations[y][4] + "+" + locations[y][5] + "%7C"
				url = url[:-3]
			url += "&destination=" + locations[z][0] + "+" + str(locations[z][1]) + "+" + locations[z][2] + "+" + \
				   locations[z][3] + "+" + locations[z][4] + "+" + locations[z][5]
			urls.append(url)
	return urls


# for testing purposes only
if __name__ == '__main__':
	one = SQLHandler()
	day = "monday"
	school_id = 1
	time = "080000"
	locations = one.select_all_addresses(school_id, day, time)
	vehicle_data, location_data, driver_indices, passenger_indices, drivers, passengers = one.locations(school_id, day, time)
	matrix = createDistanceMatrix.main(one.select_all_addresses(school_id, day, time))
	routes, dropped_nodes = Algorithm.main(vehicle_data, location_data, matrix)
	routes_temp = copy.deepcopy(routes)
	urls = construct_route_url(locations, routes_temp)
	for u in urls:
		print(u)
	temp1, temp2 = build_list(urls, routes, dropped_nodes, driver_indices, passenger_indices, drivers, passengers, day, time)
	filepath, filename = fill_data_matrix(school_id, day, time, temp1, temp2)
	one.close()
	sftp_upload(filepath, filename)