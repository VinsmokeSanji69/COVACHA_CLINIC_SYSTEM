import socket
import json
import uuid
# import psutil
from functools import lru_cache
from datetime import datetime, date

import psutil
import psutils

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow these server's MAC addresses (uppercase, colon-separated)
TRUSTED_SERVER_MACS = {
    "74:04:F1:4E:E6:02",
    "40:1A:58:BF:52:B8",
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
    """Get the MAC address of the active network interface"""
    try:
        # Get all network interfaces
        interfaces = psutil.net_if_addrs()

        # Preferred interface names (order matters)
        preferred_interfaces = ['Wi-Fi', 'Ethernet', 'eth0', 'wlan0']

        for interface in preferred_interfaces:
            if interface in interfaces:
                for addr in interfaces[interface]:
                    if addr.family == psutil.AF_LINK:
                        mac = addr.address.replace('-', ':').upper()
                        if mac.count(':') == 5:  # Validate MAC format
                            return mac

        # Fallback to first non-loopback interface with a MAC
        for interface, addrs in interfaces.items():
            if interface.lower() != 'lo' and not interface.startswith('Bluetooth'):
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        mac = addr.address.replace('-', ':').upper()
                        if mac.count(':') == 5:
                            return mac

        # Final fallback to UUID method
        mac = hex(uuid.getnode())[2:].zfill(12).upper()
        return ':'.join(mac[i:i + 2] for i in range(0, 12, 2))

    except Exception:
        # Fallback if psutil fails
        mac = hex(uuid.getnode())[2:].zfill(12).upper()
        return ':'.join(mac[i:i + 2] for i in range(0, 12, 2))


@lru_cache(maxsize=16)
def normalize_mac(mac):
    """Normalize MAC to uppercase colon-separated format"""
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac


def discover_server():
    """
    Discover the server on the network by broadcasting a discovery request
    and waiting for responses from trusted MAC addresses
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)  # Wait up to 5 seconds for a response

        # Include our MAC address in the discovery request
        client_mac = get_mac_address()
        discovery_msg = json.dumps({
            "type": "DISCOVERY_REQUEST",
            "client_mac": client_mac,
            "timestamp": datetime.now().isoformat()
        })

        try:
            s.sendto(discovery_msg.encode(), ("<broadcast>", PORT_DISCOVERY))
        except Exception as e:
            print(f"❌ Failed to send discovery request: {e}")
            return None

        try:
            while True:
                try:
                    data, addr = s.recvfrom(65535)

                    try:
                        response = json.loads(data.decode())
                        server_ip = addr[0]
                        server_mac = normalize_mac(response.get("mac", ""))

                        if not server_mac:
                            continue

                        if server_mac in TRUSTED_SERVER_MACS:
                            return server_ip
                        else:
                            print(f"⚠️ Untrusted server MAC: {server_mac} (trusted MACs: {TRUSTED_SERVER_MACS})")
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Invalid discovery response: {e}")
                        continue

                except socket.timeout:
                    print("⌛ No response received within timeout period")
                    break
                except Exception as e:
                    print(f"❌ Error receiving response: {e}")
                    continue

        except Exception as e:
            print(f"❌ Discovery process failed: {e}")

        print("❌ No trusted server found")
        return None


def send_command(command, *args, **kwargs):
    server_ip = discover_server()
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

                # Standardize response format
                if isinstance(response, (int, float, str)):
                    response = response
                elif response is None:
                    response = None

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