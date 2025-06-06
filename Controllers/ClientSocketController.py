import socket
import json
import uuid
from functools import lru_cache

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow this server's MAC address (uppercase, colon-separated)
TRUSTED_SERVER_MACS = {
    "40:1A:58:BF:52:B8"
}

def get_mac_address():
    mac = hex(uuid.getnode())[2:].zfill(12).upper()
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))

@lru_cache(maxsize=16)
def normalize_mac(mac):
    # Normalize MAC to uppercase colon-separated format
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac

def discover_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)
        s.sendto("DISCOVERY_REQUEST".encode(), ("<broadcast>", PORT_DISCOVERY))
        print("Broadcasting discovery request...")

        try:
            while True:
                data, addr = s.recvfrom(65535)
                response = json.loads(data.decode())
                server_ip = addr[0]
                server_mac = normalize_mac(response["mac"])

                print(f"Found server: {server_mac} at {server_ip}")

                if server_mac in TRUSTED_SERVER_MACS:
                    print(f"✅ Trusted server found: {server_mac}")
                    return server_ip
        except socket.timeout:
            print("❌ No trusted server found.")
            return None

def send_command(command, args=None):
    server_ip = "192.168.1.8"

    payload = command
    if args:
        try:
            json_args = json.dumps(args)
            payload = f"{command} {json_args}"
        except Exception as e:
            return {"status": "error", "message": f"Invalid arguments: {e}"}

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((server_ip, PORT_COMMAND))
            s.sendall(payload.encode())

            # Buffer the entire response
            buffer = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk

            if not buffer:
                return {"status": "error", "message": "Empty response from server"}

            logging.debug(f"Received raw response: {buffer.decode()}")

            try:
                response = json.loads(buffer.decode())
                if not isinstance(response, (dict, list)):
                    return {"status": "error", "message": "Server returned non-JSON or unsupported format"}
                return response
            except json.JSONDecodeError:
                return {"status": "error", "message": "Failed to decode JSON response"}

    except (socket.timeout, ConnectionRefusedError) as e:
        return {"status": "error", "message": f"Communication failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


class DataRequest:
    @staticmethod
    def send_command(command, args=None):
        return send_command(command, args)
