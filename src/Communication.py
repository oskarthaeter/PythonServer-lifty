#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ftp client protocol upload
import paramiko as paramiko

import Json


def sftp_upload(path, filename):
	host, username, password = Json.get_config_sftp()
	port = 22
	transport = paramiko.Transport((host, port))
	transport.connect(username=username, password=password)
	sftp = paramiko.SFTPClient.from_transport(transport)
	sftp.put(path, filename)  # Upload file to root FTP folder
	sftp.close()
	transport.close()