from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket

class RelayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            host = data.get('host')
            port = int(data.get('port', 80))
            if not host:
                raise ValueError("Missing host")
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return

        try:
            with socket.create_connection((host, port), timeout=5) as s:
                # Send HTTP GET request
                req = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                s.sendall(req.encode())
                response = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
            # Extract body (after double CRLF)
            html = response.split(b'\r\n\r\n', 1)[-1]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html)
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b'Error relaying request')

def run(server_class=HTTPServer, handler_class=RelayHandler, port=9000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Relay server listening on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
