import socket
import time
import struct

START_COMMAND = 0
PAUSE_COMMAND = 1
FINISH_COMMAND = 2

UDP_IP = "192.168.0.255"  # Широковещательный адрес
UDP_PORT = 61111

# Создаем сокет
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Разрешаем использовать широковещательный адрес
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def send_data(state, seconds, distance, data):
    # 1 - 8 header
    # 9 state
    # 10 - 13 seconds
    # 14 - 15 distance
    # 16 amount
    header = 'BRTS100'
    str_format = '<8sBIHB'

    # every 6 bytes describe
    # 16 + 6 * i + 1 to 16 + 7 * i + 4 id
    # 16 + 6 * i + 5 weight
    # 16 + 6 * i + 6 age
    parametrs_amount = 3
    n = len(data) // parametrs_amount
    str_parameters_describe = 'IBB'
    str_format = str_format + str_parameters_describe * n


    data_to_send = struct.pack(str_format, header.encode('utf-8'), state, seconds, distance, n, *data)
    return data_to_send

def send_udp_to_trainer(state_, info):

    status_str_to_int = {'go': 0, 'three': 1, 'finish': 2, 'on_start': 1, 'ready':1 }
    data = []
    for i, track in info.tracks.items():
        if track.trainer_id != 0:
            data.append(track.trainer_id)
            data.append(track.weight)
            data.append(track.age)

    print(info.race_status)
    print(status_str_to_int[info.race_status])
    data2 = send_data(status_str_to_int[info.race_status], 0, info.get_distance_meters(), data)
    print(data2)
    if data2 != 0:
        sock.sendto(data2, (UDP_IP, UDP_PORT))


if __name__ == '__main__':
    pass

