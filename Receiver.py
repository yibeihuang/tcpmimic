__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import sockets
import struct

#-------------------------Classes----------------------
class receiver:
    def __init__(self, filename, listening_port, sender_ip, sender_port, log_filename):
        self.log_filename = log_filename
        self.local_port = listening_port
        self.remote_port = sender_port
        self.recv_seq = 0
        self.send_seq = 0
        ############################Receiving###########################
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvsock.bind((sender_ip, listening_port))

        ############################Sending#############################     
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sendsock.connect((sender_ip, sender_port))
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

    def send_ack(self, ack):
        header = self.gen_header()
        self.sendsock.send(header)

    def check_chksum(pkt, chksum):
        return True         #not implemented yet

    def gen_header(self):
        header = struct.pack('HHIIBBHHH',self.local_port, self.remote_port, self.send_seq, self.recv_seq, 0, 0, 0, 0, 0)
        chksum = self.get_chksum(header, seq)
        return struct.pack('HHIIBBHHH', self.local_port, self.remote_port, self.send_seq, self.recv_seq, 0, 0, 0, chksum, 0)

    def parse_header(header_packed):
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
                self.send_ack(self.recv_seq+ 1)
                self.recv_seq += 1
            if header['flag'] & 0x1 == 1:   #FIN
                break

def main(argv):
    receive_hdlr = receiver(argv)

if __name__ == "__main__":
    #receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>
    main(sys.argv[1:])












