import socket
import struct
import time

from logger import create_logger


stop_udp_flag = False

def stop_udp_recieve():
    global stop_udp_flag
    stop_udp_flag = True

def receive_udp_from_trainer(update_func,  udp_address = ("192.168.137.1", 62222)):
    global stop_udp_flag

    UDP_IP = udp_address[0]
    UDP_PORT =  udp_address[1]

    client_header = "BRTC101"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))
    str_format = "<8s I B B B B B 3s f f f f f"
    
    while not stop_udp_flag:
        try:
            data, addr = sock.recvfrom(10240)  # Буфер 1024 байта, вы можете увеличить его при необходимости
        except:
            print ("Error")

        received_byte = struct.unpack(str_format, data)
        if(len(received_byte) != 13):           # Количество элементов в пакете. Не байт
            continue
        
        header, id, state, massHuman, ageHuman, lane, swimmingGroup, reserve, distance, time, speed, acceleration, boatTime = received_byte

        if header.decode().replace('\0', '') != client_header:
            continue

        update_func(lane, id, state, distance, time, speed, acceleration, boatTime)

udp_logger = create_logger('udp.log', use_formatter=False)
start_time =  time.time()
def update_func(lane, id, state, distance, time2, speed, acceleration, boatTime):
    global udp_logger, start_time

    timestamp_ms = int((time.time() - start_time) * 1000) # Получаем текущий таймстемп в миллисекундах
    print(f"id:{id}, state: {state}, distance: {distance}, lane: {lane}, time: {time}, speed: {speed}, acceleration: {acceleration}")
    udp_logger.info(f'{timestamp_ms} {int(time2*1000)} {int(boatTime * 1000)} {int(distance*1000)} {int(speed*1000)} {int(acceleration * 1000)}')
    pass

if __name__ == '__main__':
    receive_udp_from_trainer(update_func)
