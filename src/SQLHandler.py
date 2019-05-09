import mysql.connector as conn

# class for handling various sql queries
from src.Json import get_config_db


class SQLHandler:
	# gets sensitive login data from a json config file
	user, password, host, database = get_config_db()
	sql = None

	# initiates the class by connecting to the db
	def __init__(self):
		self.connect()

	# connects to the mysql db
	def connect(self):
		try:
			self.sql = conn.connection.MySQLConnection(user=self.user, password=self.password, host=self.host,
													   database=self.database)
			print("Connected successfully")
		except conn.Error:
			print("Connection failed")

	# prints the result of a select query
	def select(self, query):
		cursor = self.sql.cursor()
		cursor.execute(query)
		result = cursor.fetchall()
		print(result)

	def select_capacities(self, school_id, day, time):
		capacities = []
		cursor = self.sql.cursor()
		cursor.execute(
			"SELECT seats FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NOT NULL GROUP BY users.id".format(
				day, str(time), school_id))
		result = cursor.fetchall()
		for i in result:
			capacities.append(int(i[0]))
		return capacities

	# returns a list of lists of the result of a query,
	# where a row is represented as one list and the result is the list containing the row lists
	def select_all_locations(self, query):
		locations = []
		cursor = self.sql.cursor()
		cursor.execute(query)
		result = cursor.fetchall()
		for x in result:
			locations.append(list(x))
		# print(locations)
		return locations

	# returns all addresses(school, drivers and passengers) for the given parameters(school_id, day, time) in a list of lists
	# in the format: output = school address + drivers addresses + passengers address
	def select_all_addresses(self, school_id, day, time):
		passengers = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NULL GROUP BY users.id".format(
				day, str(time), school_id))
		drivers = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NOT NULL GROUP BY users.id".format(
				day, str(time), school_id))
		depot = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM schools WHERE id={}".format(
				school_id))
		locations = depot + drivers + passengers
		return locations

	# parameters day, school_id
	# format    ("monday", int)
	# returns times (list(str))
	def build_time_pool(self, day, school_id):
		pool = []
		cursor = self.sql.cursor()
		cursor.execute("SELECT DISTINCT {} FROM timetable, users WHERE users.school_id={} AND users.id=timetable.id GROUP BY users.id".format(day, school_id))
		result = cursor.fetchall()
		for x in result:
			pool.append(str(x[0]))
		return pool

	# parameters timezone
	# format     (int)
	# returns school indices (list(int))
	def build_school_pool(self, timezone):
		pool = []
		cursor = self.sql.cursor()
		cursor.execute("SELECT DISTINCT id FROM schools WHERE timezone={}".format(timezone))
		result = cursor.fetchall()
		for x in result:
			pool.append(int(x[0]))
		return pool

	# parameters None
	# returns timezones (list(int))
	def build_timezone_pool(self):
		pool = []
		cursor = self.sql.cursor()
		cursor.execute("SELECT DISTINCT timezone FROM schools")
		result = cursor.fetchall()
		for x in result:
			pool.append(int(x[0]))
		return pool

	# parameters school_id, day, time
	# format     (int, "monday", "080000")
	# returns driver indices(list(int))
	def get_driver_indices(self, school_id, day, time):
		pool = []
		cursor = self.sql.cursor()
		cursor.execute(
			"SELECT timetable.id FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NOT NULL GROUP BY users.id".format(
				day, str(time), school_id))
		result = cursor.fetchall()
		for x in result:
			pool.append(int(x[0]))
		return pool

	# parameters school_id, day, time
	# format     (int, "monday", "080000")
	# returns passenger indices(list(int))
	def get_passenger_indices(self, school_id, day, time):
		pool = []
		cursor = self.sql.cursor()
		cursor.execute(
			"SELECT timetable.id FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NULL GROUP BY users.id".format(
				day, str(time), school_id))
		result = cursor.fetchall()
		for x in result:
			pool.append(int(x[0]))
		return pool

	# parameters school_id, day, time
	# format     (int, "monday", "080000")
	# returns passenger indices(list(int)) and driver indices(list(int))
	def get_user_indices(self, school_id, day, time):
		return self.get_driver_indices(school_id, day, time), self.get_passenger_indices(school_id, day, time)

	def driver_name(self, driver_id):
		cursor = self.sql.cursor()
		cursor.execute("SELECT forename, name FROM users WHERE id={} AND seats IS NOT NULL".format(driver_id))
		result = cursor.fetchone()
		return result[0], result[1]

	# parameters school_id, day, time
	# format     (int, "monday", "080000")
	# returns vehicle_data(dict), location_data(dict), drivers relative indices(list(int)),
	# passengers relative indices(list(int)), drivers real indices(list(int)) and passengers real indices(list(int))
	def locations(self, school_id, day, time):
		depot = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM schools WHERE id={}".format(
				school_id))
		drivers = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NOT NULL GROUP BY users.id".format(
				day, str(time), school_id))
		passengers = self.select_all_locations(
			"SELECT street, streetNumber, locality, region, zipcode, country FROM users, timetable WHERE {}=\"{}\" AND school_id={} AND users.id=timetable.id AND timetable.status=1 AND seats IS NULL GROUP BY users.id".format(
				day, str(time), school_id))
		depot_index = []
		drivers_indices = []
		passengers_indices = []
		depot_index.append(0)
		for x in range(1, len(drivers) + len(depot)):
			drivers_indices.append(x)
		for z in range((len(drivers) + len(depot)), (len(passengers) + len(drivers) + len(depot))):
			passengers_indices.append(z)
		print(depot_index)
		print(drivers_indices)
		print(passengers_indices)
		locations_indices = depot_index + drivers_indices + passengers_indices
		print(locations_indices)
		location_data = {'num': len(locations_indices), 'starts': drivers_indices}
		vehicle_data = {'num': len(drivers_indices), 'capacities': self.select_capacities(school_id, day, time)}
		temp1, temp2 = self.get_user_indices(school_id, day, time)
		return vehicle_data, location_data, drivers_indices, passengers_indices, temp1, temp2

	# closes the connection to the db
	def close(self):
		self.sql.close()