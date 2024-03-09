import socket
import time

def send_udp_broadcast():
    udp_address = ("192.168.1.133", 4567)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    start_time = time.time()
    last_time = start_time
    dt = 0
    
    while True:
        current_time = int((time.time() - start_time) * 1000)  # Time since start in milliseconds
        data = (str(current_time) + ' ' + str(dt)).encode()
        
        if len(data) <= 30:
            sock.sendto(data, udp_address)
            
        dt = current_time - last_time
        print(current_time, ' ', current_time - last_time)
        
        last_time = current_time
        
        time.sleep(0.01)  # Send every 10 ms

send_udp_broadcast()
