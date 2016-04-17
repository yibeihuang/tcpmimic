__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import socket
import time
import struct
import os
import re
import math
import struct

#----------------------Variables---------------
segment_size = 576    #choose a maximum segment size, 576 bytes
SeqNumber =0         #sequence number starts from 0
RetransTimer = 0     #retransmission timer
ACKnumber = 0              #


#calculating round trip time
alpha = 0.125
beta = 0.25
EstimatedRTT = 1
SampleRTT = 0
DevRTT = 0
TimeoutInterval = EstimatedRTT + 4*DevRTT

'''
EstimatedRTT = (1-alpha)*EstimatedRTT + alpha*SampleRTT
DevRTT = (1-beta)*DevRTT + beta*abs(SampleRTT - EstimatedRTT)
'''
class node:
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

class sender:
    """
    1. send seg
    2. shift window
    """
    def __init__(self, filename, remote_IP, remote_port, ack_port_num, log_filename, window_size):
         #sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>
        'set up the sender'

        self.filename = filename
        self.remote_IP = remote_IP
        self.remote_port = remote_port
        self.ack_port_num = ack_port_num
        self.log_filename = log_filename
        self.window_size = window_size
        self.file = ""
        self.window = []
        self.windowchunk = math.floor(self.window_size/segment_size)
        self.sending_message = []
        self.seg_size = 576
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvsock.bind('', self.ack_port_num)
        self.recvsock.listen(1)

    def get_chksum(self, header, seq):
        pkt = header + self.sending_message[seq]
        csvalue = 0
        for i in  range(0, len(pkt), 2):
            w = (ord(pkt[i]) << 8) + (ord(pkt[i+1]))
            csvalue = csvalue + w
        csvalue = (csvalue>>16) + (csvalue & 0xffff)
        #complement and mask to 4 byte short
        csvalue = ~csvalue & 0xffff
        return csvalue

    def gen_header(self, seq, ack, fin):
        header = struct.pack('HHIIBBHHH',self.ack_port_num, self.remote_port, seq, ack, 0, fin, 0, 0, 0)
        chksum = self.get_chksum(header, seq)
        return struct.pack('HHIIBBHHH', self.ack_port_num, self.remote_port, seq, ack, 0, fin, 0, chksum, 0)

    def gen_seg(self, seq):
        return self.get_header(seq, 0, (1 if (seq == len(self.sending_message)) else 0)) + self.sending_message[seq]

    def send_seg(self, seq):
        pkt = self.gen_seq(seq)
        self.sendsock.sendto(pkt, (self.remote_IP, self.remote_port))

    def gen_msg(self):
        'segment the file'
        #check the size of the file
        statinfo = os.stat(self.filename)
        #open the file
        try:
        #small file, read into mem
            with open(self.filename, "r") as f:
                while True:
                    seg = f.read(self.seg_size)
                    if seg:
                        self.sending_message.append(seg)
                    else:
                        break
        except:
            print 'File not found'

    def write_log(self, logfile):
        'log the headers of all the received and sent packets'
        #timestamp, source, destination, Sequence #, ACK #, the flags and estimated RTT
        log = str(time.strftime('%X %x %Z')) + ' ' + \
              str(self.source) + ' ' + \
              str(self.dest) + ' ' + \
              str(self.seq) + ' ' + \
              str(self.ACKnum) + ' ' + \
              str(self.FIN) + ' ' + \
              str(EstimatedRTT) + '\n'
        with open('logfile','a') as thefile:
            thefile.write(log)

    def estimate_RTT(self, SampleRTT):
        'estimate the round trip time'
        EstimatedRTT = (1-alpha)*EstimatedRTT +  alpha*SampleRTT
        return EstimatedRTT

    def init_window(self):
        for x in range(self.window_size):
            self.window.append(node({
                'seq':      x,
                'acked':    False,
                'sent':     False,
            }))

    def enable_ack(self):
        while True:
            (clientsocket, address) = self.recvsock.accept()
            ack_num = self.recvsock.recv()
            #if ack_num duplicates tree times, retransmit
            
    def send(self):
        self.gen_msg()      #read file and split file into segs
        self.enable_ack()
        while True:
            #check and shift window
            for x in range(len(self.window)):
                if not self.window[x].sent:  #node not send,
                    self.send_seg(node.seq)
                    continue

                if self.window[x].acked:
                    for idx in range(x+1):
                        if self.window[-1].seq < len(self.sending_message):
                            self.window.append(node({
                                'seq':      self.window[-1].seq + 1,
                                'acked':    False,
                                'sent':     False,
                            }))
                    self.window = self.window[x:]

            if not self.window: #all data sent, finish
                break

def main(argv):

     #sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>
    #if len(argv != 6):
    #    print 'argument input wrong, please follow the format as below:\n'
    #    print 'sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>'
    #    sys.exit()
    #setup a UDP socket to send segment to receiver
    #regular expression determine the input is an IPv4/hostname inInternet domain notation or IPv6
    #assume to be ipv4
    #elif remote_IP :
    #    Sendsock = socket.socket(socket.AF_INET6, #IPv6
    #                         socket.SOCK_DGRAM)
    #else:
    #    print 'wrong remote_IP'
    #    sys.exit(-1)

    send_hdlr = sender()
    send_hdlr.gen_header(1,2,1)

if __name__ == "__main__":
    main(sys.argv[1:])







