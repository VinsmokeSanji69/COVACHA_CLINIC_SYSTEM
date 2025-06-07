import base64
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

# import psutil


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
    "password": "admin123"
}

# Server configuration
HOST = '0.0.0.0'
DISCOVERY_PORT = 50000
COMMAND_PORT = 6543

# Admin MAC address from your ipconfig (Wi-Fi adapter)
ADMIN_MAC_ADDRESS = "74-04-F1-4E-E6-02"


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
            print(self.server_mac)
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
        ip, port = address
        is_admin = self.is_admin_connection(ip)
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
            "GET_DOCTOR_BY_ID": Doctor.get_doctor,

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
            "UPDATE_LAB_TEST": Laboratory.update_lab_test
        }

        try:
            while True:
                data = connection.recv(4096)
                if not data:
                    break

                try:
                    client_info = json.loads(data.decode('utf-8', errors='ignore').strip())
                    client_mac = client_info.get("client_mac", "")
                    payload = client_info.get("command", "")

                    if not payload:
                        response = {"status": "error", "message": "Empty command"}
                        connection.sendall(json.dumps(response).encode('utf-8'))
                        continue

                    parts = payload.split(maxsplit=1)
                    command = parts[0].upper()
                    args_str = parts[1] if len(parts) > 1 else ""

                    if command == "PING":
                        response = {"status": "success", "message": "PONG"}
                    elif command not in db_methods:
                        raise ValueError(f"Unknown command: {command}")
                    else:
                        method = db_methods[command]

                        if args_str:
                            try:
                                args_data = json.loads(args_str)
                                if isinstance(args_data, dict):
                                    result = method(**args_data)
                                elif isinstance(args_data, list):
                                    result = method(*args_data)
                                else:
                                    result = method(args_data)
                            except json.JSONDecodeError:
                                args = [arg.strip() for arg in args_str.split(",")] if "," in args_str else [args_str]
                                result = method(*args)
                        else:
                            result = method()

                            # Handle the command result
                        if command == "GET_LAB_ATTACHMENTS_BY_CHECKUP":
                            # Special handling for lab attachments
                            processed_result = []
                            for item in result:
                                print("Raw item:", item)  # Debug logging

                                if isinstance(item, tuple) and len(item) > 0:
                                    # Handle tuple format [(None,), (<memory>,)] - keep as tuple
                                    if item[0] is None:
                                        processed_result.append((None,))
                                    else:
                                        try:
                                            binary_data = bytes(item[0])
                                            processed_result.append((
                                                base64.b64encode(binary_data).decode('utf-8'),
                                            ))
                                        except Exception as e:
                                            logging.error(f"Failed to process tuple binary data: {str(e)}")
                                            processed_result.append(None)
                                else:
                                    processed_result.append(item)

                            response = processed_result

                        elif isinstance(result, list):
                            processed_result = []
                            for item in result:
                                if isinstance(item, dict) and 'lab_attachment' in item:
                                    processed_item = item.copy()

                                    try:
                                        if item['lab_attachment'] is None:
                                            processed_item['lab_attachment'] = None
                                        else:
                                                # Convert memoryview/bytes to base64
                                            if isinstance(item['lab_attachment'], memoryview):
                                                binary_data = bytes(item['lab_attachment'])
                                            elif isinstance(item['lab_attachment'], bytes):
                                                binary_data = item['lab_attachment']
                                            else:
                                                binary_data = bytes(item['lab_attachment'])

                                            processed_item['lab_attachment'] = base64.b64encode(binary_data).decode(
                                                    'utf-8')

                                    except Exception as e:
                                        processed_item['lab_attachment'] = None
                                        processed_item['error'] = str(e)
                                        logging.error(f"Failed to process lab_attachment: {str(e)}")

                                    processed_result.append(processed_item)
                                else:
                                    processed_result.append(item)

                            response = processed_result
                        else:
                            # Normal processing for other commands
                            if isinstance(result, dict):
                                # Convert date strings to date objects
                                for field in ['chck_date', 'doc_dob', 'pat_dob', 'staff_dob']:
                                    if field in result and isinstance(result[field], str):
                                        try:
                                            result[field] = datetime.strptime(result[field], '%Y-%m-%d').date()
                                        except ValueError:
                                            pass
                            response = result if result is not None else {}

                        print("Final response:", response)

                except PermissionError as e:
                    msg = f"Permission denied: {str(e)}"
                    logging.warning(f"Admin attempt failed from {ip}: {msg}")
                    response = {
                        "status": "error",
                        "message": msg,
                        "code": "PERMISSION_DENIED"
                    }
                except Exception as e:
                    msg = f"Error processing command: {str(e)}"
                    logging.error(msg, exc_info=True)
                    response = {
                        "status": "error",
                        "message": msg
                    }

                # Send response
                try:
                    encoded_response = json.dumps(response, cls=CustomJSONEncoder).encode('utf-8')
                    logging.debug(f"Sending response: {response}")
                    connection.sendall(encoded_response)
                except Exception as e:
                    logging.error(f"Failed to send response: {e}")

        except Exception as e:
            logging.error(f"Critical error with {ip}: {str(e)}", exc_info=True)
        finally:
            connection.close()


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

            # HARDCODE THE CORRECT MAC ADDRESS HERE
            SERVER_MAC = "74:04:F1:4E:E6:02"  # From your Wi-Fi adapter

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
                                "mac": SERVER_MAC,  # Use the hardcoded MAC
                                "ip": socket.gethostbyname(socket.gethostname()),
                                "port": COMMAND_PORT,
                                "name": "ClinicServer"
                            }

                            s.sendto(json.dumps(response).encode(), addr)
                            logging.debug(f"Sent discovery response to {addr}")

                    except json.JSONDecodeError:
                        logging.warning(f"Invalid discovery request from {addr}")

                except Exception as e:
                    if self.running:  # Only log if we didn't stop intentionally
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
