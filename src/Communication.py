# Import socket module
import socket


def send_file(path):

	# local host IP '127.0.0.1'
	host = 'localhost'

	# Define the port on which you want to connect
	port = 12345

	# get socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# connect to server on local computer
	s.connect((host, port))

	# message you send to server
	f = open(path, "rb")

	# message sent to server
	l = f.read(1024)
	while (l):
		s.send(l)
		l = f.read(1024)
	f.close()

	# close the connection
	s.close()
