#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ftp client protocol upload
import logging

import paramiko as paramiko

import Json

logger_4 = logging.getLogger('PythonServer.Communication')

def sftp_upload(path, filename):
	logger_4.info('Sending file ...')
	host, username, password = Json.get_config_sftp()
	port = 22
	transport = paramiko.Transport((host, port))
	transport.connect(username=username, password=password)
	sftp = paramiko.SFTPClient.from_transport(transport)
	sftp.put(path, filename)  # Upload file to root FTP folder
	sftp.close()
	transport.close()
	logger_4.info('File sent')