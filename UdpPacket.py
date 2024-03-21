import struct
from PyQt5.QtCore import QTimer
from collections import deque



class UdpPacket:
    def __init__(self, data, addr):
        self.data = data
        self.addr = addr

        str_format = "<8s I BBBB BB2s f f f f f f"
        header, self.id, self.packetNumber, self.state, self.massHuman, self.ageHuman, self.swimmingGroup, self.lane, self.reserve, self.race_time, self.boatTime, self.distance, self.speed, self.acceleration, self.strokeRate = struct.unpack(str_format, self.data)

        self.header = header.decode().replace('\0', '')
        
class UDPPacketBuffer:
    delay_steps = 0
    def __init__(self, length=10, process_packet=None):
        self.length = length
        self.buffer = deque()
        self.process_packet = process_packet
        
    def get_from_buffer(self):
        if len(self.buffer) > 0:
            if self.delay_steps >= self.length:
                packet = self.buffer.popleft()
                if self.process_packet is not None:
                    self.process_packet(packet)
                return packet
            else:
                self.delay_steps += 1
        else:
            self.delay_steps = 0
        return None

    def add_packet_to_buffer(self, udp_packet):
        self.buffer.append(udp_packet)
