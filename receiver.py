import socket
import sys
# import select

SERVER_ADDRESS = "127.0.0.1"
PORT = int(sys.argv[1])
BUF_SIZE = 512
TIMEOUT = 3

# Start socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind socket to address and port
sock.bind((SERVER_ADDRESS, PORT))
print("UDP server listening on port " + str(PORT), file=sys.stderr)
# Listen for incoming datagrams
try:
    while True:
        # ready = select.select([sock], [], [], TIMEOUT)
        # if ready[0]:

        # Receive data from buffer
        data, addr = sock.recvfrom(BUF_SIZE)
        # Set duration until timeout
        sock.settimeout(TIMEOUT)
        # Decode binary data and write to file
        print(data.decode())
# Exit if socket timeout reached
except socket.timeout:
    print("File received, exiting.", file=sys.stderr)
    # Close socket connection
    sock.close()
# Exit if user enters CTRL + C
except KeyboardInterrupt:
    # Close socket connection
    sock.close()
