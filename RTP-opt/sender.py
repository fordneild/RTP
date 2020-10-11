###############################################################################
# sender.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################
#THIS IS THE OTP
import sys
import socket
import random
import time

from util import *

def sender(receiver_ip, receiver_port, window_size):
    #initialize variables
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MAX_DATA_SIZE = 1456 # 1500 (max ethernet) - 8 (UDP) - 20 (IP) - 16 (packet header)
    # MAX_DATA_SIZE = 16 # 1500 (max ethernet) - 8 (UDP) - 20 (IP) - 16 (packet header)
    data_remaining = True
    outstanding_awks = {}
    outstanding_awks_data = {}
    cur_seq_num = 0
    min_outstanding_awk = 0

    #connect to reciever
    changeConnectionStatus(s, receiver_ip, receiver_port, True)

    #while we are waiting for awks for packets we have sent, or we can send more things
    while len(outstanding_awks) > 0 or data_remaining:
        #if we have the capacity to read in more data, and there is more data to be read
        if(min_outstanding_awk + window_size > cur_seq_num and data_remaining):
            if(data_remaining):
                data = sys.stdin.read(MAX_DATA_SIZE)
                if(data == ""):
                    data_remaining = False
                sendPacket(s, receiver_ip, receiver_port, data, cur_seq_num)
                outstanding_awks[cur_seq_num] = time.time()
                outstanding_awks_data[cur_seq_num] = data
                cur_seq_num = cur_seq_num + 1
                #update min_oustanding_awk varibale after reading in new data (should only apply in case where was empty before)
                if(len(outstanding_awks) == 1):
                    min_outstanding_awk = outstanding_awks.keys()[0]
        #resend any packets that timed out
        for (seq_num, time_sent) in outstanding_awks.items():
            time_elapsed = time.time() - time_sent
            if(time_elapsed > 0.5):
                sendPacket(s, receiver_ip, receiver_port, outstanding_awks_data[seq_num], seq_num)
                outstanding_awks[seq_num] = time.time()
        #attempt to recieve awk
        s.settimeout(0.05)
        try:
            awk_pkt, address = s.recvfrom(2048)
            awk_ph= PacketHeader(awk_pkt[:16])
            #zero out checksum, so not used to compute next checksum
            expected_checksum = awk_ph.checksum
            awk_ph.checksum = 0
            msg = awk_pkt[16:16+awk_ph.length]
            computed_checksum = compute_checksum(awk_ph / msg)
            #if this is a valid awk
            if (awk_ph.type == 3 and expected_checksum == computed_checksum and awk_ph.seq_num in outstanding_awks):
                #remove this packet from outstanding_awk
                del outstanding_awks[awk_ph.seq_num]
                del outstanding_awks_data[awk_ph.seq_num]
                #update min_oustadning_awk, now that we removed one
                if awk_ph.seq_num == min_outstanding_awk:
                    try:
                        min_outstanding_awk = min(outstanding_awks.keys())
                    except ValueError:
                        min_outstanding_awk = cur_seq_num
        except socket.timeout, socket.error:
            pass
    #end connection with receiver
    changeConnectionStatus(s, receiver_ip, receiver_port, False)

def sendPacket(s, receiver_ip, receiver_port, data, seq_num):
    pkt_header = PacketHeader(type=2, seq_num=seq_num, length=len(data))
    pkt_header.checksum = compute_checksum(pkt_header / data)
    pkt = pkt_header / data
    s.sendto(str(pkt), (receiver_ip, receiver_port))
        


#isStart = true ==> START, isStart= false ==> END
def changeConnectionStatus(s, receiver_ip, receiver_port, isStart):
    send_data_type = 0 if isStart else 1
    awk = False
    while awk == False:
        #send out modify connection status request
        random_seq_num = random.randint(1, 4294967295)
        pkt_header = PacketHeader(type=send_data_type, seq_num=random_seq_num, length=1)
        pkt_header.checksum = compute_checksum(pkt_header / "i")
        pkt = pkt_header / "i"
        s.sendto(str(pkt), (receiver_ip, receiver_port))
        #recieve awk
        s.settimeout(0.05)
        try:
            awk_pkt, address = s.recvfrom(2048)
            awk_ph = PacketHeader(awk_pkt[:16])
            expected_checksum = awk_ph.checksum
            #zero out checksum, so not used to compute checksum
            awk_ph.checksum = 0
            msg = awk_pkt[16:16+awk_ph.length]
            computed_checksum = compute_checksum(awk_ph / msg)
            if (awk_ph.seq_num == random_seq_num and awk_ph.type == 3 and expected_checksum == computed_checksum):
                awk = True
        except socket.timeout, socket.error:
            pass

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)

if __name__ == "__main__":
    main()
