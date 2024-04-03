import struct
from PyQt5.QtCore import QTimer
from collections import deque

from logger import log_info
from regatta import RacerState

class UDPBoatState:
    Stop = 0b001 #// Нет гонки
    Start = 0b010 # // Гонка
    Preparing = 0b00001 | Stop #// Установка параметров
    Ready = 0b00010 | Stop #// Ожидание с обратным отсчётом
    Finish = 0b01000 | Stop #// Гонка закончена, дистанция пройдена
    
    def __init__(self, state, false_start):
        self.state = state
        #false_start в первом байте содержит признак неверной стартовой позиции. Определяем, что он не 0
        self.false_start = false_start != 0
        self.false_start = false_start
    
    def __repr__(self):
        if self.state == UDPBoatState.Finish:
            return RacerState.finish
        
        if self.false_start:
            return RacerState.false_start
        
        if self.state == UDPBoatState.Start:
            return RacerState.go
        
        if self.state == UDPBoatState.Stop or self.state == UDPBoatState.Preparing or self.state == UDPBoatState.Ready:
            return RacerState.ready
        
        return RacerState.error
    

class UdpPacket:
    def __init__(self, data, addr):
        self.data = data
        self.addr = addr

        str_format = "<8s I BBBB BBBB f f f f f f"
        header, self.id, self.packetNumber, self._state, self.massHuman, self.ageHuman, self.swimmingGroup, self.lane, self.falseStart, self.reserve, self.race_time, self.boatTime, self.distance, self.speed, self.acceleration, self.strokeRate = struct.unpack(str_format, self.data)

        self.state = UDPBoatState(self._state, self.reserve)

        self.header = header.decode().replace('\0', '')
        
class UDPPacketBuffer:
    delay_steps = 0
    empty_counter = 0
    def __init__(self, buf_size=10, process_packet=None, id=None):
        self.buf_size = buf_size
        self.buffer = deque()
        self.process_packet = process_packet
        self.id = id
        
    def do_process_packet(self):
        if len(self.buffer) > 0:
            if self.is_ready():
                packet = self.buffer.popleft()
                if self.process_packet is not None:
                    self.process_packet(packet)
            else:
                self.delay_steps += 1
        else:
            if self.delay_steps > 0:
                self.empty_counter += 1
                log_info(f"Buffer {self.id} is empty for {self.empty_counter} steps (delay_steps = {self.delay_steps})")
                
            self.delay_steps = 0

    def is_ready(self):
        return self.delay_steps >= self.buf_size


    def add_packet_to_buffer(self, udp_packet):
        if len(self.buffer) < 3:
            log_info(f'Buffer {self.id} add packet #{len(self.buffer)} (delay_steps = {self.delay_steps}) low buffer')
        self.buffer.append(udp_packet)
        
class UDPPacketBufferList:
    buffers = {}
    
    def __init__(self, buf_size =10, process_packet=None):
        self.buf_size = buf_size
        self.process_packet = process_packet
        
    def add_packet_to_buffer(self, udp_packet):
        if udp_packet.id not in self.buffers:
            self.buffers[udp_packet.id] = UDPPacketBuffer(self.buf_size, self.process_packet, udp_packet.lane)
        
        self.buffers[udp_packet.id].add_packet_to_buffer(udp_packet)
        
    def do_process_packet(self):
        if len(self.buffers) > 0:
            for id in self.buffers:
                self.buffers[id].do_process_packet()
