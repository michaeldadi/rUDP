import socket
import sys
import time

INPUT_FILE = sys.stdin
SERVER_ADDRESS = sys.argv[1]
PORT = int(sys.argv[2])
BUF_SIZE = 512

# Start socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set socket as non-blocking
sock.setblocking(False)
# Get initial binary buffer from stdin file
data = INPUT_FILE.buffer.read(BUF_SIZE)

total_bytes_sent = 0
packet_count = 0
total_time = 0
# While data is being read...
while data:
    start_time = time.time()
    # Send packet to receiver and return bytes sent in packet
    bytes_sent = sock.sendto(data, (SERVER_ADDRESS, PORT))
    # Total bytes sent by sender
    total_bytes_sent += bytes_sent
    # Read buffer of bytes from file
    data = INPUT_FILE.buffer.read(BUF_SIZE)
    elapsed_time = time.time() - start_time
    # Total time for sender to send packets
    total_time += elapsed_time
    # Current packet in sequence
    packet_count += 1
    kB_per_sec = (bytes_sent / elapsed_time) / 1000
    print("Packet " + str(packet_count) + ": " + str(bytes_sent) + " bytes sent in " + str(elapsed_time) + " seconds: "
          + str(kB_per_sec) + " kB/s")
# Print results
print("\nSent " + str(total_bytes_sent) + " bytes in " + str(total_time) + " seconds: "
      + str((total_bytes_sent / total_time) / 1000) + " kB/s")
# Close socket connection
sock.close()
