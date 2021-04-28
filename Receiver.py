import socket
import sys
import struct
from select import select
import os

from CircularQueue import CircularQueue

# Current host
HOST = "127.0.0.1"
# Current port
PORT = int(sys.argv[1])
# Current address
SERVER_ADDRESS = (HOST, PORT)
# Max bytes of data to send per packet
BUF_SIZE = 512
# Data window size
WIN_SIZE = 10
# Timeout limit
TIMEOUT = 30


def unpack_helper(fmt, datas):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, datas[:size]), datas[size:]


# Start socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind socket to address and port
sock.bind(SERVER_ADDRESS)
# Set socket as nonblocking
sock.setblocking(False)

# Readable sockets
inputs = [sock]
# Writable sockets
outputs = []

# Received binary data buffer
msg_queue = CircularQueue(WIN_SIZE)
# Actual packet sequence number
seq_num = 1
# Host & port tuple of sender
sender_addr = ""
out_file = os.readlink('/proc/%d/fd/1' % os.getpid())
print(out_file, file=sys.stderr)

print("UDP server listening on port " + str(PORT), file=sys.stderr)
# Listen for incoming datagrams while socket is ready
while inputs:
    readable, writable, exceptional = select(inputs, outputs, inputs, TIMEOUT)
    # If socket timeout
    if not (readable or writable or exceptional):
        break

    # If socket is readable...
    for s in readable:
        data, sender_addr = sock.recvfrom(BUF_SIZE)
        # If data is not empty
        if data:
            # Set timeout
            TIMEOUT = 3
            # for i in range(WIN_SIZE):
            # Packet sequence number
            # print(data[2], file=sys.stderr)
            recv_seq_num = struct.unpack_from('I', data)[0]
            # Packet ACK number
            recv_ack_num = struct.unpack_from('II', data)[1]
            # Data payload length
            payload_len = struct.unpack_from('III', data)[2]

            print(str(payload_len) + "NUM", file=sys.stderr)
            # Data payload
            #print(data.decode(), file=sys.stderr)
            msg = struct.unpack_from('%ds' % payload_len, data)[0]
            msg = msg[12:]
            # Calculate current ACK number
            print(len(msg), file=sys.stderr)
            # Set ACK number to sum of current sequence number, payload data length, and 12 (to account for header)
            ack_num = seq_num + len(msg) + 12
            # Add data payload to data buffer queue
            print("HEY! > " + str(msg), file=sys.stderr)
            msg_queue.enqueue(msg)
            print("\n" + str(seq_num) + " " + str(recv_seq_num) + " " + str(ack_num) + "\n", file=sys.stderr)
            # If sequence number & ACK number of packet received match calculated sequence number & ACK number
            if seq_num == recv_seq_num and ack_num == recv_ack_num:
                # data, sender_addr = sock.recvfrom(BUF_SIZE)
                if s not in outputs:
                    # Add writable child
                    outputs.append(s)
                else:
                    # Remove readable/exceptional child
                    inputs.remove(s)

                # Set sequence number for next incoming packet
            seq_num = ack_num

    # If socket is writable...
    for s in writable:
        # Send ACK once data verified & saved
        sock.sendto("ACK".encode(), sender_addr)
        print("sent ack", file=sys.stderr)
        # Save data to file
        # print(msg_queue.dequeue().decode(), end="")
        file = open(out_file, "ab")
        file.write(msg_queue.dequeue())
        file.close()
        # Remove writable child from outputs
        outputs.remove(s)

    # On exception...
    for s in exceptional:
        print("Error occurred, closing connection...", file=sys.stderr)
        # Remove readable/exceptional child
        inputs.remove(s)
        if s in outputs:
            # Remove writable child
            outputs.remove(s)
        # Close socket connection
        sock.close()

# Indicate file recv'd
print("File received, exiting...", file=sys.stderr)
# Close socket connection
sock.close()
