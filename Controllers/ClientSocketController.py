import base64
import socket
import json
import uuid
# import psutil
from functools import lru_cache
from datetime import datetime, date

import psutil

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow these server's MAC addresses (uppercase, colon-separated)
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
                        pass
        return obj


def get_mac_address():
    """Get the MAC address of the active network interface (for identification only)"""
    try:
        interfaces = psutil.net_if_addrs()
        for interface in ['Wi-Fi', 'Ethernet', 'eth0', 'wlan0']:
            if interface in interfaces:
                for addr in interfaces[interface]:
                    if addr.family == psutil.AF_LINK:
                        return addr.address.replace('-', ':').upper()
        return "unknown"
    except Exception:
        return "unknown"


@lru_cache(maxsize=16)
def normalize_mac(mac):
    """Normalize MAC to uppercase colon-separated format"""
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac


def discover_server():
    """Find servers and validate THEIR MAC (not client's)"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)

        # Send request WITHOUT client MAC
        s.sendto(json.dumps({"type": "DISCOVERY_REQUEST"}).encode(),
                 ("<broadcast>", PORT_DISCOVERY))

        while True:
            try:
                data, addr = s.recvfrom(65535)
                response = json.loads(data.decode())

                # Get SERVER'S MAC (should be 40:1A:58:BF:52:B8)
                server_mac = response.get("mac", "").upper().replace("-", ":")

                if server_mac in TRUSTED_SERVER_MACS:
                    return addr[0]  # Connect to this server

                # No else clause → silently ignore untrusted MACs

            except (socket.timeout, json.JSONDecodeError):
                break  # Exit on timeout or invalid response

    return None  # No trusted server found

def send_command(command, *args, **kwargs):
    server_ip = discover_server()
    if not server_ip:
        return {"status": "error", "message": "No trusted server found"}
    # Prepare payload based on argument types
    payload_data = None

    if args and kwargs:
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
            json_args = json.dumps(payload_data)
            payload = f"{command} {json_args}"
        except Exception as e:
            return {"status": "error", "message": f"Invalid arguments: {e}"}

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((server_ip, PORT_COMMAND))

            client_info = {
                "client_mac": get_mac_address(),
                "command": payload
            }
            s.sendall(json.dumps(client_info).encode())

            buffer = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if chunk.endswith(b'}') or chunk.endswith(b']') or chunk.endswith(b'"') or chunk.isdigit():
                    break

            if not buffer:
                return {"status": "error", "message": "Empty response from server"}

            try:
                # First try to parse as JSON
                try:
                    response = json.loads(buffer.decode(), cls=DateAwareJSONDecoder)
                except json.JSONDecodeError:
                    # If it fails, check if it's a simple value (like patient ID)
                    decoded = buffer.decode().strip()
                    if decoded.isdigit():
                        response = int(decoded)
                    else:
                        response = decoded

                # Process lab_attachment if present
                def process_lab_attachment(item):
                    if isinstance(item, dict) and 'lab_attachment' in item and isinstance(item['lab_attachment'], str):
                        try:
                            item['lab_attachment'] = memoryview(base64.b64decode(item['lab_attachment']))
                        except Exception as e:
                            item['lab_attachment_error'] = f"Failed to decode: {str(e)}"
                            item['lab_attachment'] = None
                    return item

                if isinstance(response, list):
                    response = [process_lab_attachment(item) if isinstance(item, dict) else item for item in response]
                elif isinstance(response, dict):
                    response = process_lab_attachment(response)
                else:
                    response = response

                return response

            except Exception as e:
                return {"status": "error", "message": f"Failed to process response: {str(e)}"}

    except (socket.timeout, ConnectionRefusedError) as e:
        return {"status": "error", "message": f"Communication failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}



def verify_server_connection(ip):
    """Verify if a server is responding at the given IP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, PORT_COMMAND))
            return True
    except:
        return False


class DataRequest:
    @staticmethod
    def send_command(command, *args, **kwargs):
        """Static method to send commands to the server"""
        return send_command(command, *args, **kwargs)