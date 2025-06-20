import base64
import json
import signal
import sys
import threading
import socket
import subprocess
import re
import platform
from functools import lru_cache
from json import JSONEncoder
from datetime import date, datetime

import psutil

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# Server configuration
HOST = '0.0.0.0'
DISCOVERY_PORT = 50000
COMMAND_PORT = 6543

# Admin MAC address from your ipconfig (Wi-Fi adapter)
ADMIN_MAC_ADDRESS = "74:04:F1:4E:E6:02"

@lru_cache(maxsize=16)
def normalize_mac(mac):
    """Normalize MAC to uppercase colon-separated format"""
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac

class SocketServer:
    def __init__(self, host=HOST, port=COMMAND_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.server_thread = None
        self.discovery_thread = None

        # Normalize all admin MACs (lowercase, hyphens replaced with colons)
        self.admin_mac = ADMIN_MAC_ADDRESS.lower().replace('-', ':')
              # Set defined at top of file

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
            print(f"Could not get MAC for {ip_address}: {str(e)}")
            return None

    def handle_doctor_staff(self, connection, address):
        # Import your models
        from Models.CheckUp import CheckUp
        from Models.Doctor import Doctor
        from Models.LaboratoryTest import Laboratory
        from Models.Patient import Patient
        from Models.Prescription import Prescription
        from Models.Staff import Staff
        from Models.Transaction import Transaction
        from Models.Admin import Admin

        ip, port = address

        db_methods = {
            #LOGIN
            "GET_USER": Admin.get_user,

            # PATIENT
            "GET_PATIENT_BY_NAME": Patient.get_patient_by_name,
            "GET_ALL_PATIENTS": Patient.get_all_patients,
            "GET_PATIENT_BY_ID": Patient.get_patient_by_id,
            "GET_PATIENT_DETAILS": Patient.get_patient_details,
            "CREATE_PATIENT": Patient.create_new_patient,
            "UPDATE_OR_CREATE_PATIENT": Patient.update_or_create_patient,
            "GET_PATIENT_ID": Patient.get_patient_by_name,
            "DELETE_PATIENT": Patient.delete_patient_by_id,

            # DOCTOR
            "GET_DOCTOR": Doctor.get_doctor,
            "GET_DOCTOR_BY_ID": Doctor.get_doctor,
            "COUNT_TOTAL_PATIENT_BY_DOCTOR": Doctor.count_total_patients_by_doctor,

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
            "UPDATE_TRANSACTION_STATUS": Transaction.update_transaction_status,
            "UPDATE_TRANSACTION": Transaction.update_transaction,
            "GET_TRANSACTION_BY_CHECKUP_ID": Transaction.get_transaction_by_chckid,
            "GET_ALL_TRANSACTION": Transaction.get_all_transaction,

            # PRESCRIPTIONS
            "CREATE_PRESCRIPTION": Prescription.add_presscription,
            "GET_PRESCRIPTION_BY_CHECKUP": Prescription.display_prescription,
            "UPDATE_PRESCRIPTION": Prescription.update_prescription_by_id,
            "GET_PRESCRIPTION_BY_DETAILS": Prescription.get_prescription_by_details,
            "DELETE_PRESCRIPTION": Prescription.delete_prescription_by_id,

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
                                if command in {"CREATE_PATIENT", "UPDATE_OR_CREATE_PATIENT", "CREATE_CHECKUP", "ADD_DIAGNOSIS_NOTES"}:
                                    result = method(args_data)
                                elif isinstance(args_data, dict):
                                    result = method(**args_data)  # Unpack for other methods
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
                                            print(f"Failed to process tuple binary data: {str(e)}")
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
                                        print(f"Failed to process lab_attachment: {str(e)}")

                                    processed_result.append(processed_item)
                                else:
                                    processed_result.append(item)

                            response = processed_result
                        else:
                            # Handle all response types
                            if result is None:
                                response = {}
                            elif isinstance(result, (dict, list)):
                                if isinstance(result, dict):
                                    # Convert date strings to date objects
                                    for field in ['chck_date', 'doc_dob', 'pat_dob', 'staff_dob']:
                                        if field in result and isinstance(result[field], str):
                                            try:
                                                result[field] = datetime.strptime(result[field], '%Y-%m-%d').date()
                                            except ValueError:
                                                pass
                                response = result
                            else:
                                response = result

                except PermissionError as e:
                    msg = f"Permission denied: {str(e)}"
                    print(f"Admin attempt failed from {ip}: {msg}")
                    response = {
                        "status": "error",
                        "message": msg,
                        "code": "PERMISSION_DENIED"
                    }
                except Exception as e:
                    msg = f"Error processing command: {str(e)}"
                    print(msg, exc_info=True)
                    response = {
                        "status": "error",
                        "message": msg
                    }

                # Send response
                try:
                    encoded_response = json.dumps(response, cls=CustomJSONEncoder).encode('utf-8')
                    connection.sendall(encoded_response)
                except Exception as e:
                    print(f"Failed to send response: {e}")

        except Exception as e:
            print(f"Critical error with {ip}: {str(e)}", exc_info=True)
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
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(('0.0.0.0', DISCOVERY_PORT))

            while self.running:
                try:
                    data, addr = s.recvfrom(1024)

                    try:
                        request = json.loads(data.decode())
                        if request.get("type") == "DISCOVERY_REQUEST":

                            response = {
                                "type": "DISCOVERY_RESPONSE",
                                "mac": self.admin_mac,
                                "ip": socket.gethostbyname(socket.gethostname()),
                                "port": COMMAND_PORT,
                                "name": "ClinicServer"
                            }
                            s.sendto(json.dumps(response).encode(), addr)

                    except json.JSONDecodeError:
                        print(f"Invalid discovery request from {addr}")

                except Exception as e:
                    if self.running:
                        print(f"Discovery error: {e}")

    def start(self):
        """Start both servers with signal handling"""
        if not self.running:
            self.running = True

            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

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

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stop()
        sys.exit(0)

    def stop(self):
        """Stop both servers gracefully"""
        if self.running:
            self.running = False

            # Stop command server
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((self.host, self.port))
            except Exception as e:
                print(f"Command server shutdown signal: {e}")
            self.server_thread.join(timeout=2)

            # Stop discovery server
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(1)
                    s.sendto(b'SHUTDOWN', ('localhost', DISCOVERY_PORT))
            except Exception as e:
                print(f"Discovery server shutdown signal: {e}")
            self.discovery_thread.join(timeout=2)
            print("Servers shut down successfully")