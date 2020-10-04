###############################################################################
# sender.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################

import sys
import socket
import random

from util import *

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MAX_DATA_SIZE = 1456 # 1500 (max ethernet) - 8 (UDP) - 20 (IP) - 16 (packet header)
    changeConnectionStatus(s, receiver_ip, receiver_port, True)
    
    #intially fill entire window with data
    data_window = [None] * window_size
    num_of_window_slots_filled = 0
    for i in range(window_size):
        data = sys.stdin.read(MAX_DATA_SIZE)
        if(data == ""):
            data_remaining = False
            break;    
        num_of_window_slots_filled = num_of_window_slots_filled + 1 # only increase if there was data
        data_window[i] = data
    
    while True:
        # updated time send last awk
        #if time since last awk < 500ms
            # resend whole window
        #else
            

        
    # if we get AWK before 500ms
        #reset timer
        #shift everything in window back by x = (window_start_seq_num - awk_seq_num)
        #repopulate rest of window with x more messages placed in last x slots
        #send those last x elements
    # else
        #resend entire window

    #timer



    #    read data until window full
    #    send all data in window (keep an array of send times)
    #array of times
    '''
        while sysclock < data[i] + 500ms and i < window_size:
            if get ack:
                i = ack
                read more data
                send more data
                your shifting algo
        
        resend window, reset data[i]
    ''''
    
            
    changeConnectionStatus(s, receiver_ip, receiver_port, False)
    
# inclusive start index, exclusive end index
def sendWindow(s, receiver_ip, receiver_port, window, startIndex, endIndex, startSeqNum):
    for i in range(startIndex, endIndex):
        data = window[i]
        pkt_header = PacketHeader(type=2, seq_num=startSeqNum+i, length=len(data))
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        s.sendto(str(pkt), (receiver_ip, receiver_port))



def changeConnectionStatus(s, receiver_ip, receiver_port, isStart):
    send_data_type = 0 if isStart else 1
    awk = False
    while awk == False:
        #send out modify connection status request
        random_seq_num = random.randint(-sys.maxint - 1,sys.maxint)
        pkt_header = PacketHeader(type=send_data_type, seq_num=random_seq_num, length=0)
        pkt_header.checksum = compute_checksum(pkt_header)
        s.sendto(str(pkt_header), (receiver_ip, receiver_port))
        #recieve awk 
        awk_pkt, address = s.recvfrom(2048)
        awk_ph = PacketHeader(awk_pkt[:16])
        cs = awk_ph.checksum
        #zero out checksum, so not used to compute next checksum
        awk_ph.checksum = 0
        msg = awk_pkt[16:16+awk_ph.length]
        cc = compute_checksum(awk_ph / msg)
        if (awk_ph.seq_num == random_seq_num and awk_ph.type == 3 and cs == cc):
            awk = True
            if(isStart):
                print "connection started"
            else: 
                print "connection ended"

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)


# data_remaining = True
#     seq_num=0
#     highest_awk_recieved = -1
#     while data_remaining:
#         #POPULATE WINDOW
#         data_window = [None] * window_size
#         num_of_window_slots_filled = 0
#         for i in range(window_size):
#             data = sys.stdin.read(MAX_DATA_SIZE)
#             if(data == ""):
#                 data_remaining = False
#                 break;    
#             num_of_window_slots_filled = num_of_window_slots_filled + 1 # only increase if there was data
#             data_window[i] = data
        
#         start_window = seq_num
#         end_window = start_window + min(window_size, num_of_window_slots_filled)
#         #RESEND WINDOW UNTIL ITS ASKING FOR NEXT WINDOW
#         while(highest_awk_recieved < end_window):
#             seq_num = start_window # reset to start of window
#             for i in range(num_of_window_slots_filled):
#                 # SEND EACH PACKET IN WINDOW
#                 data = data_window[i]
#                 pkt_header = PacketHeader(type=2, seq_num=seq_num, length=len(data))
#                 pkt_header.checksum = compute_checksum(pkt_header / data)
#                 pkt = pkt_header / data
#                 s.sendto(str(pkt), (receiver_ip, receiver_port))
#                 seq_num = seq_num + 1

#             # NOW LETS TRY TO GET THE AWKS FOR EACH PACKET WE SENT
#             # s.settimeout(0.5)
#             for i in range(num_of_window_slots_filled):
#                 # set timeout per recieve or set timeout once
#                 s.settimeout(0.5)
#                 try:
#                     awk_pkt, address = s.recvfrom(2048)
#                     awk_pkt_header = PacketHeader(awk_pkt[:16])
#                     awk_pkt_header_checksum = awk_pkt_header.checksum
#                     #zero out checksum, so not used to compute next checksum
#                     awk_pkt_header.checksum = 0
#                     msg = awk_pkt[16:16+awk_pkt_header.length]
#                     awk_checksum = compute_checksum(awk_pkt_header / msg)
#                     # p.type 3 equals AWK
#                     if (awk_pkt_header.type == 3 and cs == cc):
#                         # Then this is a valid AWK
#                         print "recieved awk for" + str(awk_pkt_header.seq_num)
#                         highest_awk_recieved = max(highest_awk_recieved, awk_pkt_header.seq_num)
#                 except (socket.timeout, socket.error):
#                     print "socket time out error"
#                     pass

if __name__ == "__main__":
    main()
