from http.server import BaseHTTPRequestHandler, HTTPServer
import json


response_data = {'message': 'Hello, World!'}

logger = None

class MyHandler(BaseHTTPRequestHandler):
        
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
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_json = json.dumps(response_data)
            self.wfile.write(response_json.encode())
            logger.info('Get Response distance: ' + str(response_data['tracks'][1]['distance']))
        else:
            self.send_error(404)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print('Starting server...')
    httpd.serve_forever()