import socket
import struct

ON=1
OFF=2
# EXAMPLE FOR YRC1000

# from yrc1000 import YRC1000
# ON = 1
# OFF = 2
# robot = YRC1000(ip="192.168.1.10", timeout=3)

# --- Servo / Hold / HLock Control ---
# robot.servo(ON)
# robot.servo(OFF)
# robot.hold(ON)
# robot.hold(OFF)
# robot.hlock(ON)
# robot.hlock(OFF)

# --- System Info / Status ---
# version = robot.get_yas_version()
# status = robot.get_status()
# job = robot.read_executing_job()
# axis_cfg = robot.read_axis_configuration()
# mgmt_time = robot.read_management_time()

# --- Alarm ---
# alarm = robot.read_alarm()
# alarm_history = robot.read_alarm_history()
# alarm_subcode = robot.read_alarm_subcode()
# alarm_history_subcode = robot.read_alarm_history_subcode()
# robot.alarm_reset()

# --- Motion Data ---
# pos = robot.read_position()
# pos_err = robot.read_position_error()
# torque = robot.read_torque()

# --- Temperature / Power ---
# encoder_temp = robot.read_encoder_temperature()
# regen_power = robot.read_regenerative_power()
# converter_temp = robot.read_converter_temperature()

# --- I/O (single) ---
# io_value = robot.read_io(1000)
# robot.write_io(1000, 1)

# --- Register (single) ---
# reg_value = robot.read_register(10)
# robot.write_register(10, 1234)

# --- Variable Access (single variable) ---
# b_val = robot.read_byte_variable(1)
# i_val = robot.read_integer_variable(1)
# d_val = robot.read_double_integer_variable(1)
# r_val = robot.read_real_variable(1)
# s_val = robot.read_string_variable(1)
# p_val = robot.read_position_variable(1)
# s32_val = robot.read_string32_variable(1)

# --- Plural I/O ---
# io_list = robot.plural_read_io(start_no=1000, count=10)

# --- Plural Register ---
# reg_list = robot.plural_read_register(start_no=1, count=5)

# --- Plural Variables ---
# b_list = robot.plural_read_byte_variable(start_no=1, count=5)
# i_list = robot.plural_read_integer_variable(start_no=1, count=5)
# d_list = robot.plural_read_double_variable(start_no=1, count=3)
# r_list = robot.plural_read_real_variable(start_no=1, count=5)
# s_list = robot.plural_read_string_variable(start_no=1, count=3)
# p_list = robot.plural_read_position_variable(start_no=1, count=3)
# bp_list = robot.plural_read_base_position_variable(start_no=1, count=2)
# ex_list = robot.plural_read_station_variable(start_no=1, count=2)
# s32_list = robot.plural_read_string32_variable(start_no=1, count=2)

# --- Move Instruction ---
# robot.move_cartesian(group_no=1, position_data=[100,200,300,0,0,0])
# robot.move_pulse(group_no=1, pulse_data=[1000,2000,3000,0,0,0])

# --- Display Message ---
# robot.display_message("HELLO WORLD")

# --- Mode Switch ---
# robot.mode_switch(0x01)  # ตัวอย่างเปลี่ยน mode

# --- Job Control ---
# robot.job_select("MAINJOB")
# robot.job_start()

# --- Close Connection ---
# robot.close()

class YRC1000:
    def __init__(self, ip, timeout=3):
        self.ip = ip
        self.control_port = 10040
        self.file_port = 10041
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_sock.settimeout(timeout)
        self.file_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_sock.settimeout(timeout)
        self.request_id = 0
        self.yas_version = None

    def _build_request(self, command_no, instance=1, attribute=0x00, service=0x01, data=b'', processing_division=0x01):
        identifier = b'YERC'
        header_size = 0x0020
        data_size = len(data)
        reserve1 = 0x03
        ack = 0x00
        request_id = self.request_id % 256
        block_no = 0x00000000
        reserve2 = b'99999999'
        sub_header = struct.pack('<H H B B H', command_no, instance, attribute, service, 0)
        header = struct.pack('<4s H H B B B B I 8s', identifier, header_size, data_size, reserve1, processing_division, ack, request_id, block_no, reserve2) + sub_header
        self.request_id += 1
        return header + data

    def _send_command(self, command_no, instance=1, attribute=0x00, service=0x01, data=b'', file_mode=False):
        processing_division = 0x02 if file_mode else 0x01
        packet = self._build_request(command_no, instance, attribute, service, data, processing_division)
        sock = self.file_sock if file_mode else self.control_sock
        port = self.file_port if file_mode else self.control_port
        sock.sendto(packet, (self.ip, port))
        response, _ = sock.recvfrom(16384)
        return response

    def get_yas_version(self):
        response = self._send_command(0x71)
        if response[20] != 0x00:
            raise Exception("System Info Read Error: " + response.hex())
        yas_ver_str = response[60:68].decode('ascii').strip()
        self.yas_version = yas_ver_str
        return yas_ver_str

    def get_status(self):
        response = self._send_command(0x72)
        if response[20] != 0x00:
            raise Exception("Status Read Error: " + response.hex())
        status = struct.unpack('<H', response[32:34])[0]
        return status

    def read_alarm(self):
        response = self._send_command(0x70)
        if response[20] != 0x00:
            raise Exception("Alarm Read Error: " + response.hex())
        alarm_no = struct.unpack('<H', response[32:34])[0]
        return alarm_no

    def read_alarm_history(self):
        response = self._send_command(0x71)
        if response[20] != 0x00:
            raise Exception("Alarm History Read Error: " + response.hex())
        return response[32:]

    def read_executing_job(self):
        response = self._send_command(0x73)
        if response[20] != 0x00:
            raise Exception("Executing Job Read Error: " + response.hex())
        job_name = response[32:40].decode('ascii').strip()
        return job_name

    def read_axis_configuration(self):
        response = self._send_command(0x74)
        if response[20] != 0x00:
            raise Exception("Axis Config Read Error: " + response.hex())
        axis_count = response[32]
        return axis_count

    def read_position(self):
        response = self._send_command(0x75)
        if response[20] != 0x00:
            raise Exception("Position Read Error: " + response.hex())
        data_len = len(response) - 32
        axis_count = data_len // 4
        position_data = struct.unpack('<' + 'i'*axis_count, response[32:32+axis_count*4])
        return position_data

    def read_position_error(self):
        response = self._send_command(0x76)
        if response[20] != 0x00:
            raise Exception("Position Error Read Error: " + response.hex())
        data_len = len(response) - 32
        axis_count = data_len // 4
        pos_error = struct.unpack('<' + 'i'*axis_count, response[32:32+axis_count*4])
        return pos_error

    def read_torque(self):
        response = self._send_command(0x77)
        if response[20] != 0x00:
            raise Exception("Torque Read Error: " + response.hex())
        data_len = len(response) - 32
        axis_count = data_len // 4
        torque_data = struct.unpack('<' + 'i'*axis_count, response[32:32+axis_count*4])
        return torque_data

    def read_io(self, io_no):
        response = self._send_command(0x78, instance=io_no)
        if response[20] != 0x00:
            raise Exception("IO Read Error: " + response.hex())
        io_value = struct.unpack('<B', response[32:33])[0]
        return io_value

    def write_io(self, io_no, value):
        data = struct.pack('<B', value)
        response = self._send_command(0x78, instance=io_no, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("IO Write Error: " + response.hex())
        return True

    def read_register(self, reg_no):
        response = self._send_command(0x79, instance=reg_no)
        if response[20] != 0x00:
            raise Exception("Register Read Error: " + response.hex())
        reg_value = struct.unpack('<i', response[32:36])[0]
        return reg_value

    def write_register(self, reg_no, value):
        data = struct.pack('<i', value)
        response = self._send_command(0x79, instance=reg_no, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Register Write Error: " + response.hex())
        return True

    def alarm_reset(self):
        response = self._send_command(0x82, service=0x02)
        if response[20] != 0x00:
            raise Exception("Alarm Reset Error: " + response.hex())
        return True

    def servo(self, state):
        if state not in (1, 2):
            raise ValueError("Invalid servo state: must be ON=1 or OFF=2")
        data = struct.pack('B', state)
        response = self._send_command(0x83, instance=2, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Servo command error: " + response.hex())
        return True

    def hold(self, state):
        if state not in (1, 2):
            raise ValueError("Invalid hold state: must be ON=1 or OFF=2")
        data = struct.pack('B', state)
        response = self._send_command(0x83, instance=1, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Hold command error: " + response.hex())
        return True

    def hlock(self, state):
        if state not in (1, 2):
            raise ValueError("Invalid hlock state: must be ON=1 or OFF=2")
        data = struct.pack('B', state)
        response = self._send_command(0x83, instance=3, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("HLock command error: " + response.hex())
        return True

    def servo_on_off(self, on=True):
        value = b'\x01' if on else b'\x02'
        response = self._send_command(0x83, service=0x02, data=value)
        if response[20] != 0x00:
            raise Exception("Servo ON/OFF Error: " + response.hex())
        return True

    def mode_switch(self, mode):
        data = struct.pack('<B', mode)
        response = self._send_command(0x84, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Mode Switch Error: " + response.hex())
        return True

    def display_message(self, message):
        text = message.encode('ascii').ljust(80, b'\x00')
        response = self._send_command(0x85, service=0x02, data=text)
        if response[20] != 0x00:
            raise Exception("Display Message Error: " + response.hex())
        return True

    def job_start(self):
        response = self._send_command(0x86, service=0x02)
        if response[20] != 0x00:
            raise Exception("Job Start Error: " + response.hex())
        return True

    def job_select(self, job_name):
        name = job_name.encode('ascii').ljust(32, b'\x00')
        response = self._send_command(0x87, service=0x02, data=name)
        if response[20] != 0x00:
            raise Exception("Job Select Error: " + response.hex())
        return True

    def read_management_time(self):
        response = self._send_command(0x88)
        if response[20] != 0x00:
            raise Exception("Management Time Read Error: " + response.hex())
        time_data = response[32:]
        return time_data

    def read_encoder_temperature(self):
        self._check_yas_version("2.9")
        response = self._send_command(0x0411)
        if response[20] != 0x00:
            raise Exception("Encoder Temp Read Error: " + response.hex())
        data_len = len(response) - 32
        axis_count = data_len // 2
        temps = struct.unpack('<' + 'h'*axis_count, response[32:32+axis_count*2])
        temps_celsius = [t / 10.0 for t in temps]
        return temps_celsius

    def read_regenerative_power(self):
        self._check_yas_version("2.9")
        response = self._send_command(0x0412)
        if response[20] != 0x00:
            raise Exception("Regen Power Read Error: " + response.hex())
        regen = struct.unpack('<H', response[32:34])[0]
        return regen

    def read_converter_temperature(self):
        self._check_yas_version("2.9")
        response = self._send_command(0x0413)
        if response[20] != 0x00:
            raise Exception("Converter Temp Read Error: " + response.hex())
        temp = struct.unpack('<h', response[32:34])[0]
        return temp / 10.0

    def _check_yas_version(self, min_version="2.9"):
        if self.yas_version is None:
            self.get_yas_version()
        current = tuple(map(int, self.yas_version.split('.')))
        required = tuple(map(int, min_version.split('.')))
        if current < required:
            raise Exception(f"YAS version {self.yas_version} is lower than required {min_version}")

    # Variable Access (Single Variable)

    def read_byte_variable(self, var_no):
        response = self._send_command(0x7A, instance=var_no)
        if response[20] != 0x00:
            raise Exception("Byte Variable Read Error: " + response.hex())
        value = struct.unpack('<B', response[32:33])[0]
        return value

    def read_integer_variable(self, var_no):
        response = self._send_command(0x7B, instance=var_no)
        if response[20] != 0x00:
            raise Exception("Integer Variable Read Error: " + response.hex())
        value = struct.unpack('<i', response[32:36])[0]
        return value

    def read_double_integer_variable(self, var_no):
        response = self._send_command(0x7C, instance=var_no)
        if response[20] != 0x00:
            raise Exception("Double Integer Variable Read Error: " + response.hex())
        value = struct.unpack('<q', response[32:40])[0]
        return value

    def read_real_variable(self, var_no):
        response = self._send_command(0x7D, instance=var_no)
        if response[20] != 0x00:
            raise Exception("Real Variable Read Error: " + response.hex())
        value = struct.unpack('<f', response[32:36])[0]
        return value

    def read_string_variable(self, var_no):
        response = self._send_command(0x7E, instance=var_no)
        if response[20] != 0x00:
            raise Exception("String Variable Read Error: " + response.hex())
        value = response[32:48].decode('ascii').rstrip('\x00')
        return value

    def read_position_variable(self, var_no):
        response = self._send_command(0x7F, instance=var_no)
        if response[20] != 0x00:
            raise Exception("Position Variable Read Error: " + response.hex())
        pos_data = struct.unpack('<' + 'i' * 6, response[32:32 + 24])
        return pos_data

    # Batch (Plural Variable Access)

    def plural_read_io(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x300, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural IO Read Error: " + response.hex())
        io_values = list(response[32:32 + count])
        return io_values

    def plural_read_register(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x301, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Register Read Error: " + response.hex())
        reg_values = struct.unpack('<' + 'i' * count, response[32:32 + 4 * count])
        return reg_values

    def plural_read_byte_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x302, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Byte Variable Read Error: " + response.hex())
        values = list(response[32:32 + count])
        return values

    def plural_read_integer_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x303, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Integer Variable Read Error: " + response.hex())
        values = struct.unpack('<' + 'i' * count, response[32:32 + 4 * count])
        return values

    def plural_read_double_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x304, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Double Variable Read Error: " + response.hex())
        values = struct.unpack('<' + 'q' * count, response[32:32 + 8 * count])
        return values

    def plural_read_real_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x305, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Real Variable Read Error: " + response.hex())
        real_values = struct.unpack('<' + 'f' * count, response[32:32 + 4 * count])
        return real_values

    def plural_read_string_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x306, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural String Variable Read Error: " + response.hex())
        values = []
        for i in range(count):
            text = response[32 + i * 16: 32 + (i + 1) * 16].decode('ascii').rstrip('\x00')
            values.append(text)
        return values

    def plural_read_position_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x307, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Position Variable Read Error: " + response.hex())
        values = []
        for i in range(count):
            pos = struct.unpack('<' + 'i' * 6, response[32 + i * 24: 32 + (i + 1) * 24])
            values.append(pos)
        return values

    def plural_read_base_position_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x308, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Base Position Variable Read Error: " + response.hex())
        values = []
        for i in range(count):
            pos = struct.unpack('<' + 'i' * 6, response[32 + i * 24: 32 + (i + 1) * 24])
            values.append(pos)
        return values

    def plural_read_station_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x309, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural Station Variable Read Error: " + response.hex())
        values = []
        for i in range(count):
            pos = struct.unpack('<' + 'i' * 6, response[32 + i * 24: 32 + (i + 1) * 24])
            values.append(pos)
        return values

    # Alarm Sub-code
    def read_alarm_subcode(self):
        response = self._send_command(0x30A)
        if response[20] != 0x00:
            raise Exception("Alarm Subcode Read Error: " + response.hex())
        alarm_data = response[32:]
        return alarm_data

    def read_alarm_history_subcode(self):
        response = self._send_command(0x30B)
        if response[20] != 0x00:
            raise Exception("Alarm History Subcode Read Error: " + response.hex())
        history_data = response[32:]
        return history_data

    def plural_read_string32_variable(self, start_no, count):
        data = struct.pack('<HH', start_no, count)
        response = self._send_command(0x30C, instance=1, data=data)
        if response[20] != 0x00:
            raise Exception("Plural 32-byte String Variable Read Error: " + response.hex())
        values = []
        for i in range(count):
            text = response[32 + i * 32: 32 + (i + 1) * 32].decode('ascii').rstrip('\x00')
            values.append(text)
        return values

    # Move Instruction
    def move_cartesian(self, group_no, position_data):
        data = struct.pack('<' + 'i' * 6, *position_data)
        response = self._send_command(0x8A, instance=group_no, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Move Cartesian Error: " + response.hex())
        return True

    def move_pulse(self, group_no, pulse_data):
        data = struct.pack('<' + 'i' * 6, *pulse_data)
        response = self._send_command(0x8B, instance=group_no, service=0x02, data=data)
        if response[20] != 0x00:
            raise Exception("Move Pulse Error: " + response.hex())
        return True

    # 32-byte String Variable Access
    def read_string32_variable(self, var_no):
        response = self._send_command(0x8C, instance=var_no)
        if response[20] != 0x00:
            raise Exception("32-byte String Variable Read Error: " + response.hex())
        value = response[32:64].decode('ascii').rstrip('\x00')
        return value

    def close(self):
        self.control_sock.close()
        self.file_sock.close()
