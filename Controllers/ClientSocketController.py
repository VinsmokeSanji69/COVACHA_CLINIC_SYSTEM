import socket
import json
import uuid
from functools import lru_cache
from datetime import datetime, date

from socket_server import CustomJSONEncoder

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow this server's MAC address (uppercase, colon-separated)
TRUSTED_SERVER_MACS = {
    "40:1A:58:BF:52:B8"
}


class DateAwareJSONDecoder(json.JSONDecoder):
    """Custom JSON decoder that converts specific date fields to datetime.date objects"""
    DATE_FIELDS = {'chck_date', 'doc_dob', 'pat_dob', 'staff_dob'}

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict):
            for key in obj:
                if key in self.DATE_FIELDS and obj[key] and isinstance(obj[key], str):
                    try:
                        obj[key] = datetime.strptime(obj[key], '%Y-%m-%d').date()
                    except (ValueError, AttributeError):
                        pass  # Keep original value if parsing fails
        return obj


def get_mac_address():
    mac = hex(uuid.getnode())[2:].zfill(12).upper()
    return ':'.join(mac[i:i + 2] for i in range(0, 12, 2))


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


def send_command(command, *args, **kwargs):
    """
    Send a command to the server with flexible argument handling.

    Args:
        command (str): The command to execute
        *args: Positional arguments (will be converted to a list)
        **kwargs: Keyword arguments (will be converted to a dict)

    Returns:
        dict: Response from server with converted date fields
    """
    server_ip = discover_server()

    # Prepare payload based on argument types
    payload_data = None

    if args and kwargs:
        # Combine positional and keyword arguments
        payload_data = {'args': args, **kwargs}
    elif args:
        # Handle positional arguments only
        if len(args) == 1 and isinstance(args[0], (dict, list)):
            payload_data = args[0]  # Single dict/list argument
        else:
            payload_data = list(args)  # Multiple positional arguments
    elif kwargs:
        # Handle keyword arguments only
        payload_data = kwargs

    # Build the payload
    payload = command
    if payload_data is not None:
        try:
            json_args = json.dumps(payload_data, cls=CustomJSONEncoder)
            payload = f"{command} {json_args}"
        except Exception as e:
            return {"status": "error", "message": f"Invalid arguments: {e}"}

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Increased timeout
            s.connect((server_ip, PORT_COMMAND))
            s.sendall(payload.encode())

            buffer = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if chunk.endswith(b'}') or chunk.endswith(b']'):
                    break

            if not buffer:
                return {"status": "error", "message": "Empty response from server"}

            try:
                response = json.loads(buffer.decode(), cls=DateAwareJSONDecoder)
                return response
            except json.JSONDecodeError:
                return {"status": "error", "message": "Failed to decode JSON response"}

    except (socket.timeout, ConnectionRefusedError) as e:
        return {"status": "error", "message": f"Communication failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


class DataRequest:
    @staticmethod
    def send_command(command, *args, **kwargs):
        return send_command(command, *args, **kwargs)