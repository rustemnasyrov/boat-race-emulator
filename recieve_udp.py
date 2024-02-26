import socket
import struct
import time

from logger import create_logger


stop_udp_flag = False

def stop_udp_recieve():
    global stop_udp_flag
    stop_udp_flag = True

def receive_udp_from_trainer(update_func):
    global stop_udp_flag
    HEADER_START_BYTE = 0
    HEADER_END_BYTE = 7
    ID_BYTES = 8
    STATE_BYTE = 9
    LANE_BYTE = 10

    TIME_BYTES = 13
    DISTANCE_BYTES = 12
    SPEED_BYTES = 14


    UDP_IP = "0.0.0.0"  # Слушаем на всех интерфейсах
    UDP_PORT = 62222  # Порт, который вы хотите использовать

    client_header = "BRTC100"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))
    str_format = "8s I B B B B B 3s f f f f"#'<BBBBBBBBiBBHfff'
    
    while not stop_udp_flag:
        try:
            data, addr = sock.recvfrom(10240)  # Буфер 1024 байта, вы можете увеличить его при необходимости
        except:
            print ("Error")

        received_byte = struct.unpack(str_format, data)
        if(len(received_byte) != 37):
            continue
        
        header, id, state, massHuman, ageHuman, lane, swimmingGroup, reserve, distance, time, speed, acceleration = unpacked_data

        header = ''
        for i in range(HEADER_START_BYTE, HEADER_END_BYTE):
            header = header + chr(received_byte[i])

        if header != client_header:
            continue

      #  id = received_byte[ID_BYTES]
      #  state = received_byte[STATE_BYTE]
      #  lane = received_byte[LANE_BYTE]


      #  time = received_byte[TIME_BYTES]
      #  distance = received_byte[DISTANCE_BYTES]
      #  speed = received_byte[SPEED_BYTES]
        update_func(lane, id, state, distance, time, speed, acceleration)

udp_logger = create_logger('udp.log', use_formatter=False)

def update_func(lane, id, state, distance, time, speed, acceleration):
    global udp_logger
    timestamp_ms = int(time.time() * 1000)  # Получаем текущий таймстемп в миллисекундах
    print(f"id:{id}, state: {state}, distance: {distance}, lane: {lane}, time: {time}, speed: {speed}")
    udp_logger.info(f'{timestamp_ms}  {int(time*1000)} {int(speed*1000)} {int(distance*1000)} {int(acceleration)}')
    pass

if __name__ == '__main__':
    receive_udp_from_trainer(update_func)
