import socket
import json
import uuid
from functools import lru_cache

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

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
    server_ip = "192.168.1.8"  # your server IP here

    # Compose payload: "COMMAND JSON_ARGS" or just "COMMAND"
    if args:
        try:
            json_args = json.dumps(args)
        except Exception as e:
            return {"status": "error", "message": f"Invalid arguments for command: {e}"}
        payload = f"{command} {json_args}"
    else:
        payload = command

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((server_ip, PORT_COMMAND))
            s.sendall(payload.encode())

            # Read full response
            buffer = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                # Optional: break early if we detect the end of JSON
                if chunk.endswith(b'}') or chunk.endswith(b']'):
                    break

            response = buffer.decode('utf-8')
            return json.loads(response)

    except (socket.timeout, ConnectionRefusedError, json.JSONDecodeError) as e:
        return {"status": "error", "message": f"Communication failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

class DataRequest:
    @staticmethod
    def send_command(command, args=None):
        return send_command(command, args)