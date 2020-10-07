###############################################################################
# sender.py
# Name: Yu-Chung Peng, Hanford Neild
# JHED ID: ypeng22, hneild1
###############################################################################

import sys
import socket
import random
import time

from util import *

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    #initialize variables
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MAX_DATA_SIZE = 1456 # 1500 (max ethernet) - 8 (UDP) - 20 (IP) - 16 (packet header)
    data_remaining = True
    need_awk = True
    data_window = [None] * window_size
    num_of_window_slots_filled = 0
    highest_awk_recieved = -1
    seq_num_at_window_start = 0

    #connect to reciever
    changeConnectionStatus(s, receiver_ip, receiver_port, True)

    #populate window with initial data
    for i in range(window_size):
        data = sys.stdin.read(MAX_DATA_SIZE)
        if(data == ""):
            data_remaining = False
            break;    
        num_of_window_slots_filled = num_of_window_slots_filled + 1 # only increase if there was data
        data_window[i] = data
    #send initial window
    sendWindow(s, receiver_ip, receiver_port, data_window, 0, num_of_window_slots_filled, seq_num_at_window_start)
    
    timer_start = time.time()
    #main processing loop
    # while there is data that has not been awked (thus still in data_window)
    while num_of_window_slots_filled != 0:
        time_elapsed = time.time() - timer_start
        if time_elapsed > .5:
            print "half second elapsed"
            print "resending whole window"
            # resend window
            sendWindow(s, receiver_ip, receiver_port, data_window, 0, num_of_window_slots_filled, seq_num_at_window_start)
            #reset clock
            timer_start = time.time()
        else:
            #recieve awk (this part im not sure about, we are potentially calling recvfrom more times than we need to)
            awk_pkt, address = s.recvfrom(2048)
            awk_ph = PacketHeader(awk_pkt[:16])
            expected_checksum = awk_ph.checksum
            #zero out checksum, so not used to compute next checksum
            awk_ph.checksum = 0
            msg = awk_pkt[16:16+awk_ph.length]
            computed_checksum = compute_checksum(awk_ph / msg)
            if (awk_ph.type == 3 and expected_checksum == computed_checksum):
                if(awk_ph.seq_num > highest_awk_recieved):
                    # we have a new highest awk
                    highest_awk_recieved = awk_ph.seq_num
                    #SHIFT PACKETS THAT HAVE BEEN AWKED DOWN
                    num_to_shift_down = awk_ph.seq_num - seq_num_at_window_start
                    for i in range(num_of_window_slots_filled - num_to_shift_down): # num_packets - num_to_remove = num_that_need_to_be_shifted
                        if(i+num_to_shift_down >= len(data_window)):
                            break
                        data_window[i] = data_window[i+num_to_shift_down]
                    #update variables after shifting them down
                    seq_num_at_window_start = awk_ph.seq_num
                    num_of_window_slots_filled = num_of_window_slots_filled - num_to_shift_down # lost this many window slots
                    first_open_slot = num_of_window_slots_filled
                    #GET NEW PACKETS TO REPLACE AWKED ONES
                    if data_remaining:
                        for i in range(num_to_shift_down):
                            data = sys.stdin.read(MAX_DATA_SIZE)
                            if(data == ""):
                                data_remaining = False
                                break;    
                            num_of_window_slots_filled = num_of_window_slots_filled + 1 # only increase if there was data
                            data_window[first_open_slot+i] = data #we should never hit index out of bounds since we dont fill more than we removed
                    #SEND NEW PACKETS
                    sendWindow(s, receiver_ip, receiver_port, data_window, first_open_slot, num_of_window_slots_filled, seq_num_at_window_start)
                    #reset the clock
                    timer_start = time.time()
                
            
            

        
    
            
    changeConnectionStatus(s, receiver_ip, receiver_port, False)
    
    # if we get AWK before 500ms
        #reset timer
        #shift everything in window back by x = (window_start_seq_num - awk_seq_num)
        #repopulate rest of window with x more messages placed in last x slots
        #send those last x elements
    # else
        #resend entire window
    
# inclusive start index, exclusive end index
def sendWindow(s, receiver_ip, receiver_port, window, startIndex, endIndex, startSeqNum):
    for i in range(startIndex, endIndex):
        data = window[i]
        pkt_header = PacketHeader(type=2, seq_num=startSeqNum+i, length=len(data))
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt = pkt_header / data
        s.sendto(str(pkt), (receiver_ip, receiver_port))


#isStart = true ==> START, isStart= false ==> END
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
        expected_checksum = awk_ph.checksum
        #zero out checksum, so not used to compute checksum
        awk_ph.checksum = 0
        msg = awk_pkt[16:16+awk_ph.length]
        computed_checksum = compute_checksum(awk_ph / msg)
        if (awk_ph.seq_num == random_seq_num and awk_ph.type == 3 and expected_checksum == computed_checksum):
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

if __name__ == "__main__":
    main()
