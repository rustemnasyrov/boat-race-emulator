import socket
import json

HOST = '127.0.0.1'  # локальный хост
PORT = 5555  # порт для прослушивания

# создаем сокет и связываем его с хостом и портом
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()  # начинаем прослушивание порта
    print(f"Сервер запущен и прослушивает порт {PORT}")
    
    # ждем подключения клиента
    conn, addr = s.accept()
    with conn:
        print(f"Подключение от {addr}")
        while True:
            data = conn.recv(1024)  # принимаем данные от клиента
            if not data:
                break
            decoded = data
            js = json.loads(data)
            print(f"Получены данные: {decoded} - {js}")  # выводим полученные данные в консоль
