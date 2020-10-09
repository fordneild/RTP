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
    if len(sys.argv) != 4:
        sys.exit("Usage: python receiver.py [Proxy's Port] [receiver Port] [receiver IP] ")
    proxy_port = int(sys.argv[1])
    receiver_port = int(sys.argv[2])
    receiver_ip = sys.argv[3]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', proxy_port))
    sender_port = 0
    while True:
    # receive packet
        pkt, address = s.recvfrom(2048)
        
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        r = random.randint(1, 100)
        #10% chance to not relay packet, 10% chance to corrupt a random byte
        if (r < 50):
            if r < 10:
                print "corrupting message wtih seqno " + str(pkt_header.seq_num)
                msg = 'get corrupted'
                pkt = pkt_header / msg
            if address[1] == receiver_port:
                #if this came from reciever, then send to sender
                print "Sending awk to sender with seq_num" + str(pkt_header.seq_num)
                s.sendto(str(pkt), (receiver_ip, sender_port))
            else:
                #this came from sender so pass it to reciever
                print "Message sent to reciver:"
                print msg
                sender_port = address[1]
                s.sendto(str(pkt), (receiver_ip, receiver_port))
        else:
            print "we are dropping packet with seq_no" + str(pkt_header.seq_num)


        
        
if __name__ == "__main__":
    main()
