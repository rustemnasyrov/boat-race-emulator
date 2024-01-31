from http.client import HTTPResponse
from http.server import HTTPServer
import threading
import http_responser as http_responser


class GetResponser:
    thread = 0
    httpd_server = None
    http_server_address = ('127.0.0.1', 8888)
    
    def start_http_server(self):
        self.stop_httpd_server()
        self.httpd_server = HTTPServer(self.http_server_address, http_responser.MyHandler)
        print('Starting http server on {}:{}...'.format(*self.http_server_address))
        self.httpd_server.serve_forever() 
    
    def stop_httpd_server(self):
        if self.httpd_server is not None:
            self.httpd_server.shutdown()
            
    def set_data(self, data):
        http_responser.response_data = data
        
    def stop(self):
        self.stop_httpd_server()
        self.thread.join()
                
    @staticmethod
    def start_thread():
        server = GetResponser()
        server.thread  = threading.Thread(target=server.start_http_server)
        server.thread.start()
        return server
        