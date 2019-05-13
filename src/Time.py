import datetime


def time_for_timedelta(time):
	new_time = (datetime.datetime.min + time).time()
	return new_time


def datetime_for_time(time):
	new_time = (datetime.datetime.combine(datetime.date(1, 1, 1), time))
	return new_time


def subtract_time(time, seconds):
	new_time = (time - datetime.timedelta(seconds=seconds))
	return new_time


def new_time_string_for_time(time):
	return datetime.time.strftime(time, "%H:%M:%S")


def time_in_range(start, end, x):
	"""Return true if x is in the range [start, end]"""
	if start <= end:
		return start <= x <= end
	else:
		return start <= x or x <= end


def add_timezone(time, timezone):
	temp_time = datetime_for_time(time)
	return (temp_time + datetime.timedelta(seconds=timezone)).time()