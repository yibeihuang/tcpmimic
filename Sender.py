__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import socket
import time
import struct
import os
import re
import math
from threading import Thread, Lock
import struct



class node(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

class sender:
    """
    1. send seg
    2. shift window
    """
    def __init__(self, argv): #filename, remote_IP, remote_port, ack_port_num, log_filename, window_size):
         #sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>
        #init message to be send in a list

        self.lock = Lock()
        self.sending_message = []
        self.seg_size = 576
        self.gen_msg(argv[0])
        self.window_size = int(argv[5])
        self.window = []
        self.init_window()

        #sending
        self.remote_ip = argv[1]
        self.remote_port = int(argv[2])
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #receive
        self.local_port = int(argv[3])
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recvsock.bind(('', self.local_port))
        self.recvsock.listen(1)
        #loging
        try:
            self.logfile_ptr = open(argv[4], 'w')
        except:
            pass

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
        header = struct.pack('HHIIBBHHH',self.local_port, self.remote_port, seq, ack, 0, fin, 0, 0, 0)
        chksum = self.get_chksum(header, seq)
        return struct.pack('HHIIBBHHH', self.local_port, self.remote_port, seq, ack, 0, fin, 0, chksum, 0)

    def gen_seg(self, seq):
        return self.gen_header(seq, 0, (1 if (seq == len(self.sending_message) -1) else 0)) + self.sending_message[seq]

    def send_seg(self, seq):
        pkt = self.gen_seg(seq)
        self.sendsock.sendto(pkt, (self.remote_ip, self.remote_port))

    def gen_msg(self, filename):
        try:
        #small file, read into mem
            with open(filename, "r") as f:
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

    def refresh_rtt(self, sample_rtt):
        self.rtt = (1-0.125)*self.rtt + 0.125*sample_rtt
        self.devrtt = (1-0.25)*self.devrtt + 0.25*abs(sample_rtt-self.rtt)
        self.timeout = self.rtt + 4*self.devrtt

    def init_window(self):
        for x in range(self.window_size):
            self.window.append(node({
                'seq':      x,
                'acked':    False,
                'sent':     False,
                'ts':       time(),
            }))

    def parse_header(self, header_packed):
        header = struct.unpack('HHIIBBHHH',header_packed)
        header_fields = ['src_port', 'dst_port', 'seq', 'ack', 'offset', 'flags', 'window', 'chksum', 'urg_ptr']
        return dict(zip(header_fields, header))

    def process_ack(self, conn):
        while True:
            recv = conn.recv(20)
            header = self.parse_header(recv)
            self.lock.acquire()
            for x in range(len(self.window)):
                if self.window[x].seq == header['ack'] - 1:
                    self.window[x].acked = True
                    print 'ack %d received' % header['ack']
                    sample_rtt = time() - self.window[x].ts
                    self.refresh_rtt(sample_rtt)
            self.lock.release()
            if header['flags'] & 0x1 == 1:
                break

    def enable_ack(self):
        print 'waiting for connection...\n'
        (conn, addr) = self.recvsock.accept()
        print 'received connection from'
        print addr
        t = Thread(target = self.process_ack, args=(conn,))
        t.start()

    def send(self):
        self.enable_ack()
        print 'start sending'
        while True:
            #check and shift window
            for x in range(len(self.window)):
                if not self.window[x].sent:  #node not send,
                    self.send_seg(self.window[x].seq)
                    self.window[x].sent = True
                    self.window[x].ts = time()
                    continue

                if self.window[x].acked:
                    self.lock.acquire()
                    for idx in range(x+1):
                        if self.window[-1].seq < len(self.sending_message) - 1:
                            self.window.append(node({
                                'seq':      self.window[-1].seq + 1,
                                'acked':    False,
                                'sent':     False,
                                'ts':       time(),
                            }))
                        del self.window[0]
                    self.lock.release()
                    break   #window length changed, break for loop and re-enter

                if time()-self.window[x].ts > self.timeout: # timeout retransmit
                    self.send_seg(self.window[x].seq)
                    self.window[x].ts = time()

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
    print argv
    send_hdlr = sender(argv)
    send_hdlr.send()

if __name__ == "__main__":
    main(sys.argv[1:])







