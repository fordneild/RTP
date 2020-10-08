###############################################################################
# receiver.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################

import sys
import socket
from util import *
import random 

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Proxy's Port] [Receiver Port] [Receiver IP]")
    proxy_port = int(sys.argv[1])
    receiver_port = int(sys.argv[2])
    receiver_ip = sys.argv[3]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', proxy_port))
    while True:
    # receive packet
        pkt, address = s.recvfrom(2048)
        
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]
        print "Message:"
        print msg
        
        
        r = random.randint(1, 100)]
        #10% chance to not relay packet, 10% chance to corrupt a random byte
        if (r < 90):
            (if r < 10):
                pkt[random.randint(0, len(pkt) - 2)] = '0';
            s.sendto(str(pkt), (receiver_port, receiver_ip))
        
        
if __name__ == "__main__":
    main()
