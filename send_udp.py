import socket
import time
import struct


UDP_IP = "192.168.137.255"  # Широковещательный адрес
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

def send_udp_to_trainer(state_):
    state = state_
    seconds = 0
    distance = 1000
    weight = [80, 85]
    age = [21, 35]
    id = [2200289112, 2]
    data = []
    for i in range(len(age)):
        data.append(id[i])
        data.append(weight[i])
        data.append(age[i])

    data2 = send_data(state, seconds, distance, data)
    if data2 != 0:
        sock.sendto(data2, (UDP_IP, UDP_PORT))

    print(str(state) + " sent\n")
    time.sleep(3)

if __name__ == '__main__':
    send_udp_to_trainer()

