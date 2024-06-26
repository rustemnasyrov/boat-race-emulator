import socket
import time
import struct

START_COMMAND = 0
PAUSE_COMMAND = 1
FINISH_COMMAND = 2

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
    header = 'BRTS101'
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

def send_udp_to_trainer(info, udp_address = ("192.168.137.255", 61111)):
    status_str_to_int = {'go': 0, 'three': 1, 'finish': 2, 'on_start': 1, 'ready':3, 'countdown':4, 'stop': 2, None: 2 }
    data = []
    for i, track in info.tracks.items():
        if track.trainer_id != 0:
            data.append(track.trainer_id)
            #упаковываем вес в байт
            # Convert weight to bytes
            data.append(track.weight)
            data.append(track.age)

    print(info.race_status)
    print(data)

    data2 = send_data(status_str_to_int[info.race_status], 0, info.get_distance_meters(), data)
    if data2 != 0:
        for i in range(15):
            sock.sendto(data2, udp_address)


if __name__ == '__main__':
    pass

