# Import socket module
import socket
from ftplib import FTP

# ftp client protocol upload

def ftp_upload(path, filename):
	ftp = FTP()
	host = 'ftp.debian.org'
	port = 12345
	ftp.connect(host, port)
	"""
	A function for uploading files to an FTP server
	@param path: The path to the file to upload
	"""
	with open(path, 'rb') as fobj:
		ftp.storbinary('STOR ' + filename, fobj, 1024)

	ftp.quit()