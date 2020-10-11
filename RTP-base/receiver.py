###############################################################################
# receiver.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################

import sys
import socket

from util import *

def receiver(receiver_port, window_size):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    buf = [None] * (window_size - 1)
    cur_seq_num = 0
    started = 0

    while True:
        # receive packet
        pkt, address = s.recvfrom(2048)

        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
             continue
        
        #check for starting connection
        if(pkt_header.type == 0 and started == 0):
            connected_address = address
            ph = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=1)
            ph.checksum = compute_checksum(ph / "i")
            pkt = ph / "i"
            s.sendto(str(pkt), (address[0], address[1]))
        #if another sender tries to connect
        elif (pkt_header.type == 0 and started == 1):
            continue
        
        #ending the connection
        if(pkt_header.type == 1 and connected_address == address and started == 1):
            ph = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=1)
            ph.checksum = compute_checksum(ph / "i")
            pkt = ph / "i"
            s.sendto(str(pkt), (address[0], address[1]))
            cur_seq_num = 0
            started = 0

        #receive data packets
        if (pkt_header.type == 2 and connected_address == address):
            started = 1
            if (pkt_header.seq_num == cur_seq_num):
                sys.stdout.write(msg)
                sys.stdout.flush()
                i = 0

                #just checking for window_size = 1
                if len(buf) > 0:
                    #read from buffer, then shift elements in buffer by the amount that was received but not acked yet
                    while (i < len(buf) and buf[i] != None):
                        sys.stdout.write(buf[i])
                        sys.stdout.flush()
                        i += 1
                    #now shift all elements i units back
                    for j in range(len(buf)):
                        if(j+i+1<len(buf)):
                            buf[j] = buf[j + i + 1]

                    #make the end i elements empty
                    for k in range(len(buf) - (i+1), len(buf)):
                        buf[k] = None

                cur_seq_num += 1 + i
                ph = PacketHeader(type=3, seq_num=cur_seq_num, length=1)
                ph.checksum = compute_checksum(ph / "i")
                pkt = ph / "i"
                s.sendto(str(pkt), (address[0], address[1]))
               
            else:
                if (pkt_header.seq_num < cur_seq_num + window_size and pkt_header.seq_num > cur_seq_num):
                    buf[pkt_header.seq_num - cur_seq_num - 1] = msg
                ph = PacketHeader(type=3, seq_num=cur_seq_num, length=1)
                ph.checksum = compute_checksum(ph / "i")
                pkt = ph / "i"
                s.sendto(str(pkt), (address[0], address[1]))


def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
