#!/usr/bin/env python
# -*- coding: utf-8 -*-
# class for building a url linking to a google maps route
import copy
import datetime

import logging
import logging.handlers

import Communication
import Algorithm, createDistanceMatrix
import Json
import SQLHandler


LOG_FORMAT = "%(name)2s %(levelname)2s %(asctime)2s - %(message)2s"
logging.basicConfig(filename='Transmitter.log', level=logging.DEBUG, format=LOG_FORMAT, filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SocketHandler(host="127.0.0.1", port=logging.handlers.DEFAULT_TCP_LOGGING_PORT)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger_1 = logging.getLogger('PythonServer.url_constructer')

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
					url += locations[y][0] + "+" + str(locations[y][1]) + "+" + locations[y][2] + "+" + locations[y][3] + \
						   "+" + locations[y][4] + "+" + locations[y][5] + "%7C"
				url = url[:-3]
			url += "&destination=" + locations[z][0] + "+" + str(locations[z][1]) + "+" + locations[z][2] + "+" + \
				   locations[z][3] + "+" + locations[z][4] + "+" + locations[z][5]
			urls.append(url)
	return urls


# for testing purposes only
if __name__ == '__main__':
	one = SQLHandler.SQLHandler()
	day = "monday"
	school_id = 1
	time = datetime.time(8,00,00)
	locations = one.select_all_addresses(school_id, day, time)
	vehicle_data, location_data, driver_indices, passenger_indices, drivers, passengers = one.locations(school_id, day, time)
	matrix, time_matrix = createDistanceMatrix.main(one.select_all_addresses(school_id, day, time))
	routes, dropped_nodes, durations = Algorithm.main(vehicle_data, location_data, matrix, time_matrix)
	routes_temp = copy.deepcopy(routes)
	urls = construct_route_url(locations, routes_temp)
	for u in urls:
		logger_1.info(u)
	temp1, temp2 = Json.build_list(urls, routes, dropped_nodes, driver_indices, passenger_indices, drivers, passengers, day, time, durations)
	filepath, filename = Json.fill_data_matrix(school_id, day, time, temp1, temp2)
	one.close()
	Communication.sftp_upload(filepath, filename)