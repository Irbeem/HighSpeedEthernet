from yrc1000 import YRC1000

# Define constants for ON/OFF
ON = 1
OFF = 2

# Create robot connection robot IP:192.168.1.10
robot = YRC1000(ip="192.168.1.10", timeout=3)

# Basic controls
robot.servo(ON)
robot.hold(ON)
robot.hlock(ON)

# Read system info
version = robot.get_yas_version()
status = robot.get_status()
job = robot.read_executing_job()

# Read variables
b_value = robot.read_byte_variable(1)
i_value = robot.read_integer_variable(1)
real_value = robot.read_real_variable(1)

# Batch read
reg_list = robot.plural_read_register(start_no=1, count=5)
p_list = robot.plural_read_position_variable(start_no=1, count=3)

# Motion commands
robot.move_cartesian(group_no=1, position_data=[100, 200, 300, 0, 0, 0])

# Read temperatures
encoder_temp = robot.read_encoder_temperature()
converter_temp = robot.read_converter_temperature()

# Reset alarm
robot.alarm_reset()

# Close connection
robot.close()
