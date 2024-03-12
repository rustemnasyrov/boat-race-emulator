import socket
import struct
import time

UDP_IP = "192.168.1.133"
UDP_PORT = 4567

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print("Listening for UDP packets on {}:{}".format(UDP_IP, UDP_PORT))

start_time = time.time()
last_time = start_time

udp_send_time_prev = 0
while True:
    data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
   # received_time, info = struct.unpack("<Q30s", data)
    received_time = data
    
    numbers = [int(num) for num in received_time.decode('utf-8').split()]
    udp_send_time = numbers[0]
    udp_send_dt = numbers[1]
    
    received_time = udp_send_time
    
    current_time = int((time.time() - start_time) * 1000)  # Time since start in milliseconds
    print(f"{current_time} {current_time-last_time} {received_time} {udp_send_time-udp_send_time_prev}")
    udp_send_time_prev = udp_send_time
    last_time = current_time
