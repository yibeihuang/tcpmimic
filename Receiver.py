__author__ = 'yibeihuang'

#---------------------Source Import--------------------
import sys
import socket
import struct
import time
from time import strftime

#-------------------------Classes----------------------
class receiver:
    def __init__(self, argv):
        #receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>
        filename, listening_port, sender_ip, sender_port, log_filename = argv
        self.log_filename = log_filename
        self.local_port = int(listening_port)
        self.remote_port = int(sender_port)
        self.recv_seq = 0
        self.send_seq = 0
        ############################Receiving###########################
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvsock.bind(('', int(listening_port)))

        ############################Sending#############################     
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sendsock.connect((sender_ip, self.remote_port))
        ############################Savd File###########################             
        try:
            self.file_ptr = open(filename, 'wb')
        except:
            pass
        ############################Log File############################
        if argv[4] == 'stdout':
            self.log_ptr = sys.stdout
        else:
            try:
                self.log_ptr = open(argv[4], 'w')
            except:
                print 'unable to write log file'
          

    def write_file(self, data):
        self.file_ptr.write(data)

    def write_log(self, header, direction, status):
        timestamp = strftime("%d,%b,%Y %H:%M:%S", time.localtime())
        log = str(timestamp) + ' '+ str(header['src_port'])+' '+ str(header['dst_port'])+' '+ str(header['seq']) +' '+ str(header['ack'])+' ' + \
                str(header['flags']) + ' ' + direction + ' '+ status + '\n'
        # with open(self.log_filename,'ab') as thefile:
        #     thefile.write(log)
        self.log_ptr.write(log)

    def send_ack(self, fin):
        header = self.gen_header(fin)
        self.sendsock.send(header)
        direction = 'send'
        status = 'ACK'
        self.write_log(self.parse_header(header), direction, status)

    def get_chksum(self, header, data):
        if data:
            pkt = header + data
        else:
            pkt = header
        csvalue = 0
        for i in range(0, len(pkt)):
            csvalue = csvalue + ord(pkt[i])
        #complement and mask to 4 byte short
        csvalue = ~csvalue & 0xffff
        return csvalue

    def check_chksum(self, pkt, chksum):
        header = pkt[:20]
        reheader = struct.unpack('HHIIBBHHH', header)
        reheader = struct.pack('HHIIBBHHH', reheader[0],reheader[1],reheader[2],reheader[3],reheader[4],reheader[5],reheader[6],0,reheader[8])
        #repkt = reheader + pkt[20:]
        rcvcsum = self.get_chksum(reheader, pkt[20:])
        if chksum == rcvcsum:
            return True
        else:
            return False

    def gen_header(self, fin):
        header = struct.pack('HHIIBBHHH',self.local_port, self.remote_port, self.send_seq, self.recv_seq + 1, 0, fin, 0, 0, 0)
        chksum = self.get_chksum(header, None)
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
            if not self.check_chksum(data, header['chksum']):   
                #bad chksum, drop packet
                print 'corrupted pkt, drop'
                direction = 'receive'
                status = 'corrupted'
                self.write_log(header, direction, status)
                continue
            #right checksum
            if header['seq'] == self.recv_seq:   #the packet we want
                direction = 'receive'
                status = 'successfully'
                self.write_log(header, direction,status)
                self.write_file(data[20:])

                self.send_ack(header['flags'] & 0x1)
                self.recv_seq += 1
            if header['flags'] & 0x1 == 1:   #FIN
                direction = 'receive'
                status = 'finalize'
                self.write_log(header, direction,status)
                self.file_ptr.close()
                break

def main(argv):
    print argv
    receive_hdlr = receiver(argv)
    receive_hdlr.receive()

if __name__ == "__main__":
    #receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>
    main(sys.argv[1:])












