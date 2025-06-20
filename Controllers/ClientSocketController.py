import base64
import socket
import json
import time
import uuid
# import psutil
from functools import lru_cache
from datetime import datetime, date

import psutil

PORT_DISCOVERY = 50000
PORT_COMMAND = 6543

# Only allow these server's MAC addresses (uppercase, colon-separated)
TRUSTED_SERVER_MACS = {
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


def test_connection_by_mac(target_mac):
    """
    Test connection to a specific machine by its MAC address (admin function)

    Args:
        target_mac (str): The MAC address of the target machine to test

    Returns:
        dict: Connection test results including:
            - status: "success" or "error"
            - message: Detailed status message
            - server_ip: IP address if found
            - reachable: Boolean indicating if server is reachable
    """
    # Normalize the target MAC address
    try:
        target_mac = normalize_mac(target_mac)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Invalid MAC address: {str(e)}",
            "server_ip": None,
            "reachable": False
        }

    # First discover all servers on network
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)

        discovery_msg = json.dumps({
            "type": "ADMIN_DISCOVERY_REQUEST",
            "client_mac": get_mac_address(),
            "timestamp": datetime.now().isoformat(),
            "admin": True
        })

        try:
            s.sendto(discovery_msg.encode(), ("<broadcast>", PORT_DISCOVERY))
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send discovery request: {str(e)}",
                "server_ip": None,
                "reachable": False
            }

        target_ip = None
        start_time = time.time()

        while time.time() - start_time < 5:  # 5 second timeout
            try:
                data, addr = s.recvfrom(65535)
                try:
                    response = json.loads(data.decode())
                    server_mac = normalize_mac(response.get("mac", ""))

                    if server_mac == target_mac:
                        target_ip = addr[0]
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
            except socket.timeout:
                break
            except Exception:
                continue

        if not target_ip:
            return {
                "status": "error",
                "message": f"Target machine with MAC {target_mac} not found on network",
                "server_ip": None,
                "reachable": False
            }

        # Now test command port connectivity
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.settimeout(2)
                test_socket.connect((target_ip, PORT_COMMAND))

                # Send test ping
                test_socket.sendall(json.dumps({
                    "client_mac": get_mac_address(),
                    "command": "PING"
                }).encode())

                # Get response
                response = test_socket.recv(1024)
                if response:
                    try:
                        response_data = json.loads(response.decode())
                        if response_data.get("message") == "PONG":
                            return {
                                "status": "success",
                                "message": "Connection test successful",
                                "server_ip": target_ip,
                                "reachable": True
                            }
                    except json.JSONDecodeError:
                        pass

                return {
                    "status": "success",
                    "message": "Server responded but with unexpected response",
                    "server_ip": target_ip,
                    "reachable": True
                }

        except socket.timeout:
            return {
                "status": "error",
                "message": "Server found but command port timed out",
                "server_ip": target_ip,
                "reachable": False
            }
        except ConnectionRefusedError:
            return {
                "status": "error",
                "message": "Server found but command port refused connection",
                "server_ip": target_ip,
                "reachable": False
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "server_ip": target_ip,
                "reachable": False
            }


def discover_server():
    """
    Discover the server on the network by broadcasting a discovery request
    and waiting for responses from trusted MAC addresses.
    Returns server IP if found, None otherwise.
    """
    if not test_network_connectivity():
        print("❌ No network connectivity detected")
        return None

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)

        # Get our MAC and IP to filter self-responses
        client_mac = get_mac_address()
        discovery_msg = json.dumps({
            "type": "DISCOVERY_REQUEST",
            "client_mac": client_mac,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())  # Unique ID for this request
        })

        try:
            s.bind(('', 0))

            # Send multiple discovery requests (3 attempts)
            for attempt in range(3):
                try:
                    s.sendto(discovery_msg.encode(), ("<broadcast>", PORT_DISCOVERY))
                    print(f"🔍 Discovery attempt {attempt + 1}/3 sent")

                    # Wait for response with decreasing timeout
                    timeout = 1.5 - (attempt * 0.3)  # 1.5s, 1.2s, 0.9s
                    s.settimeout(timeout)

                    try:
                        while True:
                            data, addr = s.recvfrom(65535)
                            server_ip = addr[0]

                            try:
                                response = json.loads(data.decode())
                                if response.get("request_id") == json.loads(discovery_msg)["request_id"]:
                                    server_mac = normalize_mac(response.get("mac", ""))
                                    if server_mac in TRUSTED_SERVER_MACS:
                                        print(f"✅ Admin server received request (attempt {attempt + 1})")
                                        print(f"📡 Server IP: {server_ip}, MAC: {server_mac}")
                                        return server_ip

                            except (json.JSONDecodeError, KeyError) as e:
                                continue

                    except socket.timeout:
                        continue

                except Exception as e:
                    print(f"⚠️ Discovery attempt {attempt + 1} failed: {e}")
                    continue

        except Exception as e:
            print(f"❌ Discovery process failed: {e}")

        print("🔴 No admin server response received")
        return None

def test_network_connectivity():
    """
    Test basic network connectivity before attempting discovery
    Returns True if basic network operations succeed
    """
    try:
        # Test DNS resolution
        socket.gethostbyname("google.com")

        # Test local network interface
        interfaces = psutil.net_if_addrs()
        if not interfaces:
            print("⚠️ No network interfaces found")
            return False

        # Test if any interface has an IP address
        has_ip = False
        for iface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                    has_ip = True
                    break
            if has_ip:
                break

        if not has_ip:
            print("⚠️ No active IP addresses found")
            return False

        return True

    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False

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