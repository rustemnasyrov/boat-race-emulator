from http.client import HTTPResponse
from http.server import HTTPServer
import http_responser as http_responser


from PyQt5.QtCore import QThread, pyqtSlot

class GetResponser(QThread):
    httpd_server = None
    http_server_address = ('127.0.0.1', 8888)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        
    @pyqtSlot()
    def run(self):
        self.start_http_server()
        
    def start_http_server(self):
        self.stop_httpd_server()
        from http.server import HTTPServer
        self.httpd_server = HTTPServer(self.http_server_address, http_responser.MyHandler)
        print('Starting http server on {}:{}...'.format(*self.http_server_address))
        self.httpd_server.serve_forever() 
    
    def stop_httpd_server(self):
        if self.httpd_server is not None:
            self.httpd_server.shutdown()
            
    @pyqtSlot(dict)
    def set_data(self, data):
        http_responser.response_data = data
        
    @pyqtSlot()
    def stop(self):
        self.stop_httpd_server()
        self.quit()
        self.wait() # wait for thread to finish
        