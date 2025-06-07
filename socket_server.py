import json
import threading
import socket
import logging
import subprocess
import re
import platform
import uuid
from functools import lru_cache
from json import JSONEncoder
from datetime import date, datetime

import psutils


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


logging.basicConfig(filename='server.log', level=logging.DEBUG)

# Import your models
from Models.CheckUp import CheckUp
from Models.Doctor import Doctor
from Models.LaboratoryTest import Laboratory
from Models.Patient import Patient
from Models.Prescription import Prescription
from Models.Staff import Staff
from Models.Transaction import Transaction

DB_CONFIG = {
    "host": "localhost",
    "database": "ClinicSystem",
    "user": "postgres",
    "password": "sphinxclub012"
}

# Server configuration
HOST = '0.0.0.0'
DISCOVERY_PORT = 50000
COMMAND_PORT = 6543

# Admin MAC address from your ipconfig (Wi-Fi adapter)
ADMIN_MAC_ADDRESS = "40-1A-58-BF-52-B8"


class SocketServer:
    def __init__(self, host=HOST, port=COMMAND_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_thread = None
        self.discovery_thread = None
        self.admin_mac = ADMIN_MAC_ADDRESS.lower().replace('-', ':')
        self.server_mac = self.admin_mac

    def _get_active_mac_address(self):
        """Get MAC address of the active network interface"""
        try:
            interfaces = psutil.net_if_addrs()
            preferred_interfaces = ['Wi-Fi', 'Ethernet', 'eth0', 'wlan0']

            for interface in preferred_interfaces:
                if interface in interfaces:
                    for addr in interfaces[interface]:
                        if addr.family == psutil.AF_LINK:
                            mac = addr.address.replace('-', ':').lower()
                            if mac.count(':') == 5:
                                return mac
            return self.server_mac  # Fallback to hardcoded MAC
        except Exception:
            return self.server_mac

    @staticmethod
    @lru_cache(maxsize=32)
    def get_mac_from_ip(ip_address):
        """Get MAC address for a given IP using ARP"""
        try:
            if platform.system() == "Windows":
                arp_output = subprocess.check_output(["arp", "-a", ip_address]).decode('utf-8', errors='ignore')
                mac_match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", arp_output)
            else:
                arp_output = subprocess.check_output(["arp", "-n", ip_address]).decode('utf-8', errors='ignore')
                mac_match = re.search(r"(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2}))", arp_output)

            if mac_match:
                return mac_match.group(0).lower().replace('-', ':')
            return None
        except Exception as e:
            logging.warning(f"Could not get MAC for {ip_address}: {str(e)}")
            return None

    def is_admin_connection(self, ip_address):
        """Check if connection is from admin device by MAC address"""
        if not ip_address:
            return False

        client_mac = self.get_mac_from_ip(ip_address)
        if not client_mac:
            return False

        return client_mac == self.admin_mac

    def handle_doctor_staff(self, connection, address):
        """Handle client connections with robust error handling"""
        ip, port = address
        is_admin = self.is_admin_connection(ip)
        print(f"Connected by {address} (Admin: {is_admin})")
        logging.info(f"Connection from {address} (Admin: {is_admin})")

        db_methods = {
            # PATIENT
            "GET_PATIENT_BY_NAME": Patient.get_patient_by_name,
            "GET_ALL_PATIENTS": Patient.get_all_patients,
            "GET_PATIENT_BY_ID": Patient.get_patient_by_id,
            "GET_PATIENT_DETAILS": Patient.get_patient_details,
            "CREATE_PATIENT": Patient.create_new_patient,
            "UPDATE_OR_CREATE_PATIENT": Patient.update_or_create_patient,
            "GET_PATIENT_ID": Patient.get_patient_by_name,

            # DOCTOR
            "GET_DOCTOR": Doctor.get_doctor,
            "GET_DOCTOR_BY_ID": Doctor.get_doctor_by_id,

            # STAFF
            "GET_STAFF": Staff.get_staff,

            # CHECKUPS
            "GET_NEXT_SEQUENCE_NUMBER": CheckUp.get_next_sequence_number,
            "CREATE_CHECKUP": CheckUp.save_checkup,
            "GET_PENDING_CHECKUP": CheckUp.get_pending_checkups,
            "UPDATE_CHECKUP_STATUS": CheckUp.update_checkup_status,
            "GET_CHECKUP_DETAILS": CheckUp.get_checkup_details,
            "GET_CHECKUP_BY_PAT_ID": CheckUp.get_checkup_by_pat_id,
            "GET_CHECKUP_BY_DOC_ID": CheckUp.get_all_checkups_by_doc_id,
            "GET_ALL_CHECKUP": CheckUp.get_all_checkups,
            "UPDATE_DOC_ID": CheckUp.update_doc_id,
            "UPDATE_LAB_CODES": CheckUp.update_lab_codes,
            "GET_TEST_BY_CHECK_ID": CheckUp.get_test_names_by_chckid,
            "UPDATE_LAB_ATTACHMENT": CheckUp.update_lab_attachment,
            "GET_LAB_ATTACHMENT": CheckUp.get_lab_attachment,
            "ADD_DIAGNOSIS_NOTES": CheckUp.add_diagnosis_notes,
            "CHANGE_STATUS_COMPLETED": CheckUp.change_status_completed,
            "GET_LAB_CODES_BY_CHECK_ID": CheckUp.get_lab_codes_by_chckid,
            "ADD_LAB_CODE": CheckUp.add_lab_code,
            "DELETE_LAB_CODE": CheckUp.delete_lab_code,
            "GET_CHECKUPS_WITH_LAB_REQUESTS": CheckUp.get_checkups_with_lab_requests,
            "GET_LAB_ATTACHMENTS_BY_CHECKUP": CheckUp.get_lab_attachments_by_checkup_id,

            # TRANSACTIONS
            "CREATE_TRANSACTION": Transaction.add_transaction,
            "UPDATE_TRANSACTION": Transaction.update_transaction,
            "GET_TRANSACTION_BY_CHECKUP_ID": Transaction.get_transaction_by_chckid1,
            "GET_ALL_TRANSACTION": Transaction.get_all_transaction,
            "UPDATE_TRANSACTION_STATUS": Transaction.update_transaction_status,

            # PRESCRIPTIONS
            "CREATE_PRESCRIPTION": Prescription.add_presscription,
            "GET_PRESCRIPTION_BY_CHECKUP": Prescription.display_prescription,

            # LABORATORY TESTS
            "GET_LAST_LAB_ID": Laboratory.get_last_lab_id,
            "GET_NEXT_LAB_ID": Laboratory.get_next_lab_id,
            "CHECK_LAB_NAME_EXISTS": Laboratory.lab_name_exists,
            "SAVE_LAB_TEST": Laboratory.save_lab_test,
            "GET_ALL_TEST": Laboratory.get_all_test,
            "GET_TEST_BY_LAB_CODE": Laboratory.get_test_by_labcode,
            "GET_LAB_CODE_BY_NAME": Laboratory.get_lab_code_by_name,
            "COUNT_ALL_TEST": Laboratory.count_all_test,
            "CHECK_LAB_CODE_EXISTS": Laboratory.lab_code_exists,
            "GET_LAB_TEST": Laboratory.get_lab_test,
            "UPDATE_LAB_TEST": Laboratory.update_lab_test,
        }

        try:
            while True:
                data = connection.recv(1024)
                if not data:
                    break

                decoded_data = data.decode('utf-8', errors='ignore').strip()
                logging.debug(f"Received raw data: {decoded_data}")

                if not decoded_data:
                    continue

                try:
                    # Improved command parsing that handles multiple formats
                    command = None
                    args = None

                    # Case 1: Pure JSON input
                    if decoded_data.startswith('{') and decoded_data.endswith('}'):
                        try:
                            json_data = json.loads(decoded_data)
                            if isinstance(json_data, dict):
                                command = json_data.get("command", "").upper()
                                args = json_data.get("args", {})
                        except json.JSONDecodeError:
                            pass

                    # Case 2: Space-separated command with arguments
                    if command is None:
                        parts = decoded_data.split(maxsplit=1)
                        command = parts[0].upper()
                        args = parts[1] if len(parts) > 1 else None

                    # Case 3: Command with brackets [10000]
                    if args and args.startswith('[') and args.endswith(']'):
                        args = args[1:-1]  # Remove brackets

                    # Process the command
                    if command == "PING":
                        response = {"status": "success", "message": "PONG"}
                    elif command not in db_methods:
                        response = {
                            "status": "error",
                            "message": f"Unknown command: {command}",
                            "valid_commands": list(db_methods.keys())
                        }
                    else:
                        method = db_methods[command]

                        try:
                            # Handle different argument formats
                            if args is None:
                                result = method()
                            elif isinstance(args, dict):
                                result = method(**args)
                            else:
                                # For space-separated arguments
                                if isinstance(args, str):
                                    args = [arg.strip() for arg in args.split(",")]
                                result = method(*args) if isinstance(args, list) else method(args)

                            # Format the response
                            if result is None:
                                response = {"status": "success"}
                            elif isinstance(result, (dict, list)):
                                response = result
                            else:
                                response = result

                        except Exception as e:
                            response = {
                                "status": "error",
                                "message": f"Error executing {command}: {str(e)}"
                            }
                            logging.error(f"Command execution error: {command}", exc_info=True)

                except Exception as e:
                    response = {
                        "status": "error",
                        "message": f"Invalid request format: {str(e)}"
                    }
                    logging.error(f"Request parsing error", exc_info=True)

                # Send response
                try:
                    encoded_response = json.dumps(response, cls=CustomJSONEncoder).encode('utf-8')
                    connection.sendall(encoded_response)
                except Exception as e:
                    logging.error(f"Failed to send response: {e}")
                    break

        except Exception as e:
            logging.error(f"Critical error in connection handler: {e}", exc_info=True)
        finally:
            try:
                connection.close()
            except:
                pass
            logging.info(f"Connection closed with {address}")

    def _run_server(self):
        """Main command server loop"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"✅ Command server running on {self.host}:{self.port}")

            while self.running:
                conn, addr = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_doctor_staff,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()

    def _run_discovery_server(self):
        """Handle UDP discovery requests with fixed MAC address"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(('0.0.0.0', DISCOVERY_PORT))
            print(f"🔍 Discovery server running (MAC: {self.server_mac})")

            while self.running:
                try:
                    data, addr = s.recvfrom(1024)
                    ip, port = addr

                    try:
                        request = json.loads(data.decode())
                        if request.get("type") == "DISCOVERY_REQUEST":
                            client_mac = request.get("client_mac", "unknown")
                            logging.info(f"Discovery request from {ip} (Client MAC: {client_mac})")

                            response = {
                                "type": "DISCOVERY_RESPONSE",
                                "mac": self.server_mac,  # Always use the hardcoded MAC
                                "ip": socket.gethostbyname(socket.gethostname()),
                                "port": COMMAND_PORT,
                                "name": "ClinicServer"
                            }

                            s.sendto(json.dumps(response).encode(), addr)
                            logging.debug(f"Sent discovery response to {addr}")

                    except json.JSONDecodeError:
                        logging.warning(f"Invalid discovery request from {addr}")

                except Exception as e:
                    if self.running:
                        logging.error(f"Discovery error: {e}")

    def start(self):
        """Start both servers"""
        if not self.running:
            self.running = True

            # Start command server
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()

            # Start discovery server
            self.discovery_thread = threading.Thread(
                target=self._run_discovery_server,
                daemon=True
            )
            self.discovery_thread.start()

            print(f"🚀 Servers started - Discovery: {DISCOVERY_PORT}, Commands: {COMMAND_PORT}")

    def stop(self):
        """Stop both servers gracefully"""
        if self.running:
            self.running = False

            # Stop command server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, COMMAND_PORT))
            self.server_thread.join(timeout=1)

            # Stop discovery server
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(b'', ('localhost', DISCOVERY_PORT))
            self.discovery_thread.join(timeout=1)
            print("🛑 Servers stopped")