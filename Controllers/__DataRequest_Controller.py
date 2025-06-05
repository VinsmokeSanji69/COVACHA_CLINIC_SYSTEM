import socket
import json

HOST = "192.168.101.6"  # Admin computer's IP
PORT = 5433

class DataRequest:
    @staticmethod
    def send_command(command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
            data = s.recv(4096).decode()
            return json.loads(data)
