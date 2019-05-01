# Import socket module
import socket
from ftplib import FTP

# ftp client protocol upload
import paramiko as paramiko


def ftp_upload(path, filename):
	ftp = FTP()
	host = ''
	port = 22
	ftp.connect(host, port)
	ftp.login("", "")
	"""
	A function for uploading files to an FTP server
	@param path: The path to the file to upload
	"""
	with open(path, 'rb') as fobj:
		ftp.storbinary('STOR ' + filename, fobj, 1024)

	ftp.quit()


def sftp_upload(path, filename):
	host = ''
	port = 22
	transport = paramiko.Transport((host, port))
	transport.connect(username="", password="")
	sftp = paramiko.SFTPClient.from_transport(transport)
	sftp.put(path, filename)  # Upload file to root FTP folder
	sftp.close()
	transport.close()
