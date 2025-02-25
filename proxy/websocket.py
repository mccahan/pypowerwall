import http.server
import socketserver
import threading
import hashlib
import base64
import struct

class WebSocketHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get("Upgrade") == "websocket":
            self.handle_websocket()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"This is a simple HTTP server, use a WebSocket client to connect.\n")

    def handle_websocket(self):
         # WebSocket handshake
        key = self.headers.get("Sec-WebSocket-Key")
        if key:
            digest = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode('utf-8')).digest())
            self.send_response(101)
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", digest.decode('utf-8'))
            self.end_headers()

            # WebSocket communication
            while True:
                try:
                    data = self.receive_websocket_data()
                    if not data:
                        break  # Connection closed
                    print("Received:", data.decode('utf-8'))
                    self.send_websocket_data(data) # Echo back
                except ConnectionResetError:
                    break

    def receive_websocket_data(self):
        # Receive WebSocket data with handling fragmentation and control frames
        header = self.rfile.read(2)
        if len(header) < 2:
            return None

        fin = header[0] & 0x80
        opcode = header[0] & 0x0f
        masked = header[1] & 0x80
        payload_length = header[1] & 0x7f

        if payload_length == 126:
            payload_length = struct.unpack(">H", self.rfile.read(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack(">Q", self.rfile.read(8))[0]

        masks = self.rfile.read(4) if masked else None
        payload = self.rfile.read(payload_length)

         # Unmask the payload
        if masked:
            unmasked_payload = bytes([payload[i] ^ masks[i % 4] for i in range(len(payload))])
        else:
            unmasked_payload = payload
        
        if opcode == 0x08: # Close frame
            self.send_websocket_close()
            return None
        elif opcode == 0x01: # Text frame
            return unmasked_payload
        else:
             return bytes() # Ignore other frames

    def send_websocket_data(self, data):
        # Send WebSocket data
        frame = bytearray()
        frame.append(0x81)  # Text frame, final fragment
        payload_length = len(data)

        if payload_length < 126:
            frame.append(payload_length)
        elif payload_length < 65536:
            frame.append(126)
            frame.extend(struct.pack(">H", payload_length))
        else:
            frame.append(127)
            frame.extend(struct.pack(">Q", payload_length))

        frame.extend(data)
        self.wfile.write(bytes(frame))

    def send_websocket_close(self):
         # Send WebSocket close frame
        self.wfile.write(bytes([0x88, 0x00]))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    PORT = 8080
    with ThreadedTCPServer(("", PORT), WebSocketHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()