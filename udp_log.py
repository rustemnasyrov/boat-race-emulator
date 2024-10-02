import socket
import time
from TimeMeter import TimeMeter
from UdpPacket import UdpPacket

from logger import create_logger
from regatta import RacerState

import csv
import os
from datetime import datetime

# Функция для создания файла с текущей датой и временем в названии
def create_csv_writer():
    # Формируем имя файла на основе текущей даты и времени
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f'udp_data_{timestamp}.csv'
    
    # Открываем файл для записи
    file = open(file_name, mode='w', newline='')
    writer = csv.writer(file)
    
    # Записываем заголовки
    writer.writerow([
        'packetNumber', 'state', 'timestamp_ms', 'dt', 'boatTime', 'dt_boat', 
        'distance', 'speed', 'race_time', 'acceleration', 
        'systemTime', 'pressCount', 'averageInterval'
    ])
    
    return writer, file

# Функция для записи данных в CSV
def append_to_csv(writer, udp_packet, timestamp_ms, dt, dt_boat):
    # Записываем данные в CSV через существующий writer
    writer.writerow([
        udp_packet.packetNumber, udp_packet.state, timestamp_ms, dt, 
        f"{udp_packet.boatTime:.4f}", f"{dt_boat:.0f}", 
        f"{udp_packet.distance:.4f}", f"{udp_packet.speed:.6f}", 
        f"{udp_packet.race_time:.4f}", f"{udp_packet.acceleration:.6f}",
        udp_packet.systemTime, udp_packet.pressCount, udp_packet.averageInterval
    ])


stop_udp_flag = False


def stop_udp_recieve():
    global stop_udp_flag
    stop_udp_flag = True


udp_logger = create_logger('udp.log', use_formatter=False)
start_time =  time.time()


def receive_udp_from_trainer(update_func, udp_address=("192.168.137.1", 61112), filter_ip = None):
    global stop_udp_flag

    UDP_IP = udp_address[0]
    UDP_PORT = udp_address[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))

    while not stop_udp_flag:
        try:
            data, addr = sock.recvfrom(10240)  # Буфер 1024 байта, вы можете увеличить его при необходимости
        except:
            print ("Error")

        if addr[0] == filter_ip or filter_ip is None:
            udp_packet = UdpPacket.unpack(data, addr)
            update_func(udp_packet)




last_timestamp = 0
last_boat_time = 0
active_id = 0

tm = {}


csv_writer = csv_file = None 

def log_update_func(udp_packet):
    global udp_logger, start_time, last_timestamp, last_boat_time, active_id, in_race, csv_writer, csv_file

    mms = tm.setdefault(udp_packet.lane, TimeMeter()).get_measure_str()
    #print(f"{udp_packet.swimmingGroup} - {udp_packet.lane} {mms}")
    #udp_logger.info(f"{udp_packet.lane} {mms}")
    tm[udp_packet.lane].update_time()   

    if (active_id == udp_packet.id or not active_id):
        if repr(udp_packet.state) == RacerState.go:
            if csv_writer is None:
                csv_writer, csv_file = create_csv_writer()
                in_race = True
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                print(f"------------------- Начало гонки {timestamp} -------------------------------")
                udp_logger.info(f"------------------- Начало гонки {timestamp} -------------------------------")

            active_id = udp_packet.id
            timestamp_ms = int((time.time() - start_time) * 1000)  # Получаем текущий таймстемп в миллисекундах
            dt = timestamp_ms - last_timestamp
            dt_boat = (udp_packet.boatTime - last_boat_time)*1000
            print(f"{udp_packet.packetNumber}, {udp_packet.state}, time:{timestamp_ms:<10} ({dt:<2}) t={udp_packet.boatTime:.4f} ({dt_boat:.0f})"
                f" S={udp_packet.distance:.4f}, v={udp_packet.speed:.6f}, t={udp_packet.race_time:.4f} a={udp_packet.acceleration:.6f}"
                f" >> sysTime={udp_packet.systemTime:<5} pressCount={udp_packet.pressCount:<5} averageInterval={udp_packet.averageInterval:<5} ")
            udp_logger.info(f'{timestamp_ms} ({dt}) {udp_packet.id} {udp_packet.packetNumber} {udp_packet.state} {int(udp_packet.race_time*1000)} ({int(dt *1000)}) {int(udp_packet.boatTime * 1000)} {int(udp_packet.distance*1000)} {int(udp_packet.speed*1000)} {int(udp_packet.acceleration * 1000)}')
            append_to_csv(csv_writer, udp_packet, timestamp_ms, dt, dt_boat)
            
            last_timestamp = timestamp_ms
            last_boat_time = udp_packet.boatTime
        else:
            if csv_file:
                csv_file.close()
                csv_writer = csv_file = None
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                print(f"++++++++++++++++++ Конец гонки {timestamp} ++++++++++++++++++++++++++")
                udp_logger.info(f"++++++++++++++++++ Конец гонки {timestamp} ++++++++++++++++++++++++++")

if __name__ == '__main__':
    receive_udp_from_trainer(update_func=log_update_func, filter_ip='192.168.137.116')

