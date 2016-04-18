__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import socket
import struct

#-------------------------Classes----------------------
class receiver:
    def __init__(self, argv):
        filename, listening_port, sender_ip, sender_port, log_filename = argv
        self.log_filename = log_filename
        self.local_port = int(listening_port)
        self.remote_port = int(sender_port)
        self.recv_seq = 0
        self.send_seq = 0
        ############################Receiving###########################
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvsock.bind((sender_ip, int(listening_port)))

        ############################Sending#############################     
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sendsock.connect((sender_ip, self.remote_port))
        ############################Savd File###########################             
        try:
            self.file_ptr = open(filename, 'w')
        except:
            pass
        ############################Log File############################
          

    def write_file(self, data):
        self.file_ptr.write(data)

    def write_log(self):
        pass

    def send_ack(self, fin):
        header = self.gen_header(fin)
        self.sendsock.send(header)

    def get_chksum(self, pkt):
        csvalue = 0
        for i in  range(0, len(pkt), 2):
            w = (ord(pkt[i]) << 8) + (ord(pkt[i+1]))
            csvalue = csvalue + w
        csvalue = (csvalue>>16) + (csvalue & 0xffff)
        #complement and mask to 4 byte short
        csvalue = ~csvalue & 0xffff
        return csvalue

    def check_chksum(self, pkt, chksum):
        return True         #not implemented yet

    def gen_header(self, fin):
        header = struct.pack('HHIIBBHHH',self.local_port, self.remote_port, self.send_seq, self.recv_seq + 1, 0, fin, 0, 0, 0)
        chksum = self.get_chksum(header)
        return struct.pack('HHIIBBHHH', self.local_port, self.remote_port, self.send_seq, self.recv_seq + 1, 0, fin, 0, chksum, 0)
        self.send_seq += 1
    def parse_header(self, header_packed):
        header = struct.unpack('HHIIBBHHH',header_packed)
        header_fields = ['src_port', 'dst_port', 'seq', 'ack', 'offset', 'flags', 'window', 'chksum', 'urg_ptr']
        return dict(zip(header_fields, header))

    def receive(self):
        while True:
            data, addr = self.recvsock.recvfrom(1024)
            header = self.parse_header(data[:20])
            if not self.check_chksum(data, header['chksum']):   #bad chksum, drop packet
                continue
            #right checksum
            if header['seq'] == self.recv_seq:   #the packet we want
                self.write_file(data[20:])
                self.send_ack(header['flags'] & 0x1)
                self.recv_seq += 1
            if header['flags'] & 0x1 == 1:   #FIN
                self.file_ptr.close()
                break

def main(argv):
    receive_hdlr = receiver(argv)
    receive_hdlr.receive()

if __name__ == "__main__":
    #receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>
    main(sys.argv[1:])












