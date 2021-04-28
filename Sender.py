import socket
import sys
import struct
from select import select
import time

from CircularQueue import CircularQueue

# Binary buffer of file from user to be read
INPUT_FILE = sys.stdin.buffer
# Target server host
HOST = sys.argv[1]
# Target server port
PORT = int(sys.argv[2])
# Server address (host & port)
SERVER_ADDRESS = (HOST, PORT)
# Max bytes of data to send per packet
BUF_SIZE = 512
# Data window size
WIN_SIZE = 10
# Timeout limit
TIMEOUT = 3


# Pack RUDP datagram into struct
def create_rudp_dgram(seq, ack, payload):
    print(str(payload))
    # Get payload data length
    str_len = len(payload.decode())
    print(str_len)
    print(payload)
    print(payload.decode())

    print(str(sys.getsizeof(payload)) + " " + str(len(payload)) + " " + str(len(str(payload))))
    # Generate RUDP datagram
    return struct.pack('III%ds' % str_len, seq, ack, str_len, payload)


# Start socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set socket as non-blocking
sock.setblocking(False)

# Circular queue to hold sent data in buffer
bin_data_buf = CircularQueue(WIN_SIZE)
# Number of total bytes of data (incl. data headers) sent
total_bytes_sent = 0
# Number of total packets currently sent
packet_count = 0
# Packet sequence number
seq_num = 1
# Total time elapsed sending file
total_time = 0

# Get initial binary buffer from stdin file
data = INPUT_FILE.read(BUF_SIZE)

# Readable sockets
inputs = []
# Writable sockets
outputs = [sock]

# While socket is ready & data is being read...
while outputs and data:
    readable, writable, exceptional = select(inputs, outputs, inputs, TIMEOUT)

    for s in readable:
        # Verify packet received with ACK
        acknowledged = False
        # While ACK not received...
        while not acknowledged:
            try:
                # Receive ACK from server
                recv_ack, addr = sock.recvfrom(BUF_SIZE)
                # Data packet has been acknowledged
                acknowledged = True
            except socket.timeout:
                # Resend datagram
                bytes_sent = sock.sendto(current_pkt, SERVER_ADDRESS)

    # If socket is writable...
    for s in writable:
        # If data is not empty
        while data:
            start_time = time.time()
            # Read buffer of bytes from file & enqueue to sender buffer
            bin_data_buf.enqueue(data)
            # Set ACK number to sequence number of next packet
            ack_num = seq_num + len(data)

            # Create RUDP datagram struct (header + payload)
            current_pkt = create_rudp_dgram(seq_num, ack_num, data)
            # Send packet to receiver and return bytes sent in packet
            bytes_sent = sock.sendto(current_pkt, SERVER_ADDRESS)

            # Record time elapsed to send 1 packet
            elapsed_time = time.time() - start_time
            # Current packet in sequence
            packet_count += 1
            # Rate of packet transfer in kB/s
            kB_per_sec = (bytes_sent / elapsed_time) / 1000

            # Print current packet stats
            print("Packet " + str(packet_count) + ": " + str(bytes_sent) + " bytes sent in " + str(elapsed_time)
                  + " seconds: " + str(kB_per_sec) + " kB/s")

            # Total bytes sent by sender
            total_bytes_sent += bytes_sent
            # Set sequence number for next packet
            seq_num = ack_num
            # Running total time for sender to send packets
            total_time += elapsed_time
            # Read data for next packet
            data = INPUT_FILE.read(BUF_SIZE)

    # On exception...
    for s in exceptional:
        print("Error occurred, closing connection...", file=sys.stderr)
        # Remove child from readable/exceptional
        inputs.remove(s)
        if s in outputs:
            # Remove child from writable
            outputs.remove(s)
        # Close socket connection
        sock.close()

# Print final results
print("\nSent " + str(total_bytes_sent) + " bytes in " + str(total_time) + " seconds: "
      + str((total_bytes_sent / total_time) / 1000) + " kB/s")

# Close socket connection
sock.close()
