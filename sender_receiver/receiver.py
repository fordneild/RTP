###############################################################################
# receiver.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################

import sys
import socket

from util import *

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    f = open("out.txt",'w')

    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    buf = [None] * (window_size - 1)
    cur_seq_num = 0
    started = 0
    while True:
        # receive packet
        pkt, address = s.recvfrom(2048)
        # sys.stdout.write("Message recieved!\n")
        # sys.stdout.flush()

        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]
        # print "Message:"
        # print msg

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
             continue

        if(pkt_header.type == 0 and started == 0):
            sys.stdout.write("STARTING CONNECTION...\n")
            connected_address = address
            ph = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=1)
            ph.checksum = compute_checksum(ph / "i")
            pkt = ph / "i"
            s.sendto(str(pkt), (address[0], address[1]))
        elif (started == 1):
            print "sender already connected. ignoring request"

        if(pkt_header.type == 1 and connected_address == address and started == 1):
            sys.stdout.write("\nENDING CONNECTION...\n")
            sys.stdout.flush()
            ph = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=1)
            ph.checksum = compute_checksum(ph / "i")
            pkt = ph / "i"
            s.sendto(str(pkt), (address[0], address[1]))
            cur_seq_num = 0
            started = 0
            f.close()

        if(pkt_header.type == 2 and connected_address == address):
            print 'recieved data packet num: ' + str(pkt_header.seq_num)
            print 'cur_seq_num: ' + str(cur_seq_num)
            started = 1
            if (pkt_header.seq_num == cur_seq_num):
                sys.stdout.write(msg)
                f.write(msg)
                sys.stdout.flush()
                i = 0
                #read from buffer, then shift elements in buffer by the amount that was received but not acked yet
                while (i < len(buf) and buf[i] != None):
                    sys.stdout.write(buf[i])
                    f.write(buf[i])
                    sys.stdout.flush()
                    i += 1

                for j in range(0, i + 1):
                    if(j+i+1<len(buf)):
                        buf[j] = buf[j + i + 1]
                # buf[0:i] = buf[i:min(2*i,len(buf))]
                for k in range(len(buf) - (i+1), len(buf)):
                    buf[k] = None
                # for k in range(len(buf) - i):
                #     buf[window_size - 2 - k] = None
                # buf[len(buf) - (i + 1): len(buf)] = [None] * (i + 1)

                cur_seq_num += 1 + i
                ph = PacketHeader(type=3, seq_num=cur_seq_num, length=1)
                ph.checksum = compute_checksum(ph / "i")
                pkt = ph / "i"
                s.sendto(str(pkt), (address[0], address[1]))
                print 'end of loop, cur_seq_num: ' + str(cur_seq_num) + 'buffer: ' + str(buf)
               
            else:
                print 'recieved data but not in order'
                print str(cur_seq_num) + " " + str(pkt_header.seq_num)

                if (pkt_header.seq_num < cur_seq_num + window_size and pkt_header.seq_num > cur_seq_num):
                    print 'putting ' + str(pkt_header.seq_num) + ' in buffer slot: ' + str(pkt_header.seq_num - cur_seq_num - 1)
                    buf[pkt_header.seq_num - cur_seq_num - 1] = msg
                #print 'cur seq num is ' + str(cur_seq_num)
                ph = PacketHeader(type=3, seq_num=cur_seq_num, length=1)
                ph.checksum = compute_checksum(ph / "i")
                pkt = ph / "i"
                s.sendto(str(pkt), (address[0], address[1]))

        # print payload
        # print msg
        # sys.stdout.write(msg)
        # sys.stdout.flush()


    #THIS CAME FROM GITHUB
    # def _split_message(self, message):
    #     pieces = message.split('|')
    #     msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
    #     checksum = pieces[-1] # last is always treated as checksum
    #     data = '|'.join(pieces[2:-1]) # everything in between is considered data
    #     return msg_type, seqno, data, checksum

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
