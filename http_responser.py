from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from TimeMeter import TimeMeter
from extropolation import BoatParameters

from logger import log_info


response_data = {'message': 'Hello, World!'}

last_get_time = time.time()
dt = 0

logger = None

_current_boat_parameters = BoatParameters(time_ms=0, speed_mm_sec=0, distance_mm=0)
lock = threading.Lock()

global_string = "Hello world"

def get_now_boat_parameters():
    global _current_boat_parameters
    if _current_boat_parameters:
        _current_boat_parameters =  _current_boat_parameters.get_next_for_now()
    return _current_boat_parameters

def set_current_boat_parameters(new_boat_parameters):
    global _current_boat_parameters
    lock.acquire()
    if not new_boat_parameters:
        return
    _current_boat_parameters = new_boat_parameters
    lock.release()

def get_current_parameters_string():
    params = get_now_boat_parameters()
    if params:
        return f'Get Response {params.distance} {global_string}'
    return '>>> ! <<<<'

response_func = get_current_parameters_string

def get_current_boat_parameters():
    return _current_boat_parameters

tm = TimeMeter()

class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        #log_info(f'Get response ({tm.get_measure_str()})')
        #tm.update_time()
        pass
    
    def do_POST(self):
       # content_length = int(self.headers['Content-Length'])
       # post_data = self.rfile.read(content_length)
       # json_data = json.loads(post_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

      #  response = {'message': 'Received JSON data:', 'data': json_data}
        response_json = json.dumps(response_data)
        self.wfile.write(response_json.encode())
        
    def do_GET(self):
        global last_get_time, dt

        lock.acquire()
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_json = json.dumps(response_data)
            self.wfile.write(response_json.encode())
 
        else:
            self.send_error(404)
        lock.release()

if __name__ == '__main__':
    server_address = ('', 8888)
    httpd = HTTPServer(server_address, MyHandler)
    print('Starting server...')
    httpd.serve_forever()