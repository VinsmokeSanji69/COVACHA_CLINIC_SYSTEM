import socket
import json
import uuid
from functools import lru_cache

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow this server's MAC address
TRUSTED_SERVER_MACS = {
    "40:1A:58:BF:52:B8"
}

def get_mac_address():
    """Returns the current device's MAC address"""
    mac = hex(uuid.getnode()).replace('0x', '').upper()
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))


@lru_cache(maxsize=16)
def normalize_mac(mac):
    """Standardize MAC format to colon-separated lowercase"""
    return mac.lower().replace('-', ':').replace('.', ':')


def discover_server():
    """
    Broadcasts discovery request and waits for trusted server response.
    Returns IP of the server if found, None otherwise.
    """
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

                if server_mac.upper() in {normalize_mac(m).upper() for m in TRUSTED_SERVER_MACS}:
                    print(f"✅ Trusted server found: {server_mac}")
                    return server_ip
        except socket.timeout:
            print("❌ No trusted server found.")
            return None


def send_command(command):
    """
    Sends a command to the trusted server and returns parsed JSON response.
    """
    server_ip = discover_server()
    if not server_ip:
        return {"status": "error", "message": "Server not found or unreachable"}

    payload = json.dumps({
        "command": command,
        "mac": get_mac_address()
    })

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((server_ip, PORT_COMMAND))
            s.sendall(payload.encode())
            response = s.recv(4096).decode()
            return json.loads(response)
    except (socket.timeout, ConnectionRefusedError, json.JSONDecodeError) as e:
        return {"status": "error", "message": f"Communication failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


class DataRequest:
    @staticmethod
    def send_command(command):
        return send_command(command)