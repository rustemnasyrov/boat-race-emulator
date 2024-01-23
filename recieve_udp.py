import socket
import struct


def recieve_udp_from_trainer(update_func):
    HEADER_START_BYTE = 0
    HEADER_END_BYTE = 7
    ID_BYTES = 8
    STATE_BYTE = 9
    LANE_BYTE = 10
    DISTANCE_BYTES = 11
    TIME_BYTES = 12
    SPEED_BYTES = 13


    UDP_IP = "0.0.0.0"  # Слушаем на всех интерфейсах
    UDP_PORT = 62222  # Порт, который вы хотите использовать

    client_header = "BRTC100"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))
    str = '<BBBBBBBBiBBHfff'
    while True:
        data, addr = sock.recvfrom(1024)  # Буфер 1024 байта, вы можете увеличить его при необходимости
        received_byte = struct.unpack(str, data)

        if(len(received_byte) != 28):
            continue

        header = ''
        for i in range(HEADER_START_BYTE, HEADER_END_BYTE):
            header = header + received_byte(data[i])

        if header != client_header:
            continue

        id = received_byte[ID_BYTES]
        state = received_byte[STATE_BYTE]
        lane = received_byte[LANE_BYTE]

        distance = received_byte[DISTANCE_BYTES]
        time = received_byte[TIME_BYTES]
        speed = received_byte[SPEED_BYTES]

        # Вывод данных
        #print("Received byte: {}".format(received_byte))
        update_func(lane, id, state, distance, time, speed)


def update_func(lane, id, state, distance, time, speed):
    print(f"id:{id}, state: {state}, distance: {distance}, lane: {lane}, time: {time}, speed: {speed}")
    pass

if __name__ == '__main__':
    recieve_udp_from_trainer(update_func)
