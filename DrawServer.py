from DrawInterpreter import DrawInterpreter

import socket
import sys
import os
import time

interpreter = DrawInterpreter()


server_address = './drawbot_uds_socket'

# Make sure the socket does not already exist
try:
	os.unlink(server_address)
except OSError:
	if os.path.exists(server_address):
		raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print >>sys.stderr, 'starting up on %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

try:
	while True:
		# Wait for a connection
		print >>sys.stderr, 'waiting for a connection'
		connection, client_address = sock.accept()
		try:
			print >>sys.stderr, '- connection from client', client_address

			alldata = ""
			# Receive the data in small chunks
			while True:
				data = connection.recv(16)
				print >>sys.stderr, '- received "%s"' % data
				if data:
					alldata+=data
				else:
					print >>sys.stderr, '- no more data from client', client_address
					break

			print >>sys.stderr, 'Running command', alldata, '...'
			interpreter.activate()
			time.sleep(1)
			interpreter.do(alldata)
			time.sleep(3)
			interpreter.deactivate()
			print >>sys.stderr, 'Finished running command.'
			print >>sys.stderr, '---------------------'

		finally:
			# Clean up the connection
			connection.close()
finally:
	sock.close()
	interpreter.deactivate()
