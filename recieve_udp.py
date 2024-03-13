import socket
import struct
import time

from logger import create_logger


stop_udp_flag = False


def stop_udp_recieve():
    global stop_udp_flag
    stop_udp_flag = True


class UdpPacket:
    def __init__(self, data, addr):
        self.data = data
        self.addr = addr

        str_format = "<8s I BBBB BB2s f f f f f f"
        header, self.id, self.packetNumber, self.state, self.massHuman, self.ageHuman, self.swimmingGroup, self.lane, self.reserve, self.race_time, self.boatTime, self.distance, self.speed, self.acceleration, self.strokeRate = struct.unpack(str_format, self.data)

        self.header = header.decode().replace('\0', '')


udp_logger = create_logger('udp.log', use_formatter=False)
start_time =  time.time()


def receive_udp_from_trainer(update_func, udp_address=("192.168.137.1", 61112)):
    global stop_udp_flag

    UDP_IP = udp_address[0]
    UDP_PORT = udp_address[1]
    client_header = "BRTC102"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))

    while not stop_udp_flag:
        try:
            data, addr = sock.recvfrom(10240)  # Буфер 1024 байта, вы можете увеличить его при необходимости
        except:
            print ("Error")

        udp_packet = UdpPacket(data, addr)

        if udp_packet.header != client_header:
            continue

        update_func(udp_packet)


last_timestamp = 0
last_boat_time = 0
active_id = 0
def log_update_func(udp_packet):
    global udp_logger, start_time, last_timestamp, last_boat_time, active_id


    if True: #active_id == udp_packet.id or not active_id:
        active_id = udp_packet.id
        timestamp_ms = int((time.time() - start_time) * 1000)  # Получаем текущий таймстемп в миллисекундах
        dt = timestamp_ms - last_timestamp
        dt_boat = udp_packet.boatTime - last_boat_time
        print(f"{timestamp_ms} ({dt}) {udp_packet.id} {udp_packet.packetNumber}, state: {udp_packet.state}, distance: {udp_packet.distance}, lane: {udp_packet.lane}, time: {udp_packet.race_time}, speed: {udp_packet.speed}, acceleration: {udp_packet.acceleration}")
        udp_logger.info(f'{timestamp_ms} ({dt}) {udp_packet.id} {udp_packet.packetNumber} {udp_packet.state} {int(udp_packet.race_time*1000)} ({int(dt *1000)}) {int(udp_packet.boatTime * 1000)} {int(udp_packet.distance*1000)} {int(udp_packet.speed*1000)} {int(udp_packet.acceleration * 1000)}')
        last_timestamp = timestamp_ms
        last_boat_time = udp_packet.boatTime

if __name__ == '__main__':
    receive_udp_from_trainer(log_update_func)

