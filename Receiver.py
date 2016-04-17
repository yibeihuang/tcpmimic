__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import socket
import thread
from threading import Thread
import time
from time import strftime
import struct

#------------------------Variables---------------------
MAXSEGMENTSIZE = 576                   # File will be divided into this size of segments to be transferred
CORRUPTION = False               # The flag of first receiving
ACK_ACK = 0                            # ACK # used to send ACK back to sender
ACK_SEQUENCE = 0                       # Sequence # used to send ACK back to sender
TRANS_FINISH = False                   # The flag to mark if the transmission is finished

#-------------------------Classes----------------------
class receiver:
    def __init__(self, filename, listening_port, sender_IP, sender_port, log_filename):
        self.filename = filename
        self.listening_port = listening_port
        self.sender_IP = sender_IP
        self.sender_port = sender_port
        self.log_filename = log_filename

    def receive(self):
        pass

    def write_file(self):
        pass

    def validate(self):
        pass

    def write_log(self):
        pass


    def send_ack(self):
        'send ack of the largest sequence number of the in order segment'
        ACKsocket.sendto(ACKdata, (self.sender_IP, self.sender_port))

if __name__ == "__main__":
    #receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>

    receiver_IP =
    listening_port = sys.argv[1:].split()[1]
    sender_IP = sys.argv[1:].split()[2]
    sender_port = sys.argv[1:].split()[3]

    #receive segment data, UDP socket
    #regular expression match
    if sender_IP == re.:
        Rcvsocket = socket.socket(socket.AF_INET, #IPv4
                                  socket.SOCK_DGRAM)
    else:
        Rcvsocket = socket.socket(socket.AF_INET6, #IPv6
                                  socket.SOCK_DGRAM)
    Rcvsocket.bind(('', listening_port))

    #send ACK data, TCP socket
    ACKsocket = socket.socket(socket.AF_INET,
                              socket.SOCK_STREAM)












