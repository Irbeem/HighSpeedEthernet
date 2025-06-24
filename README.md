Full-featured Python library for controlling and monitoring YASKAWA YRC1000 robot controllers via High-Speed Ethernet function.

## Features

- Read system status, alarm, job, management data
- Full control of servo, hold, hlock, modes
- Full variable access (B/I/D/R/S/P/BP/EX/S32)
- Full plural (batch) variable read functions
- Temperature monitoring (encoder, converter)
- Real-time position, torque, IO access
- Full move instruction support (Cartesian / Pulse)
- Full alarm sub-code reading

Requirements
Python 3.6+

YASKAWA YRC1000 Controller with High-Speed Ethernet Function activated

Robot controller firmware version YAS >= 2.9 (for temperature functions)

Note
This SDK communicates directly with the YRC1000 controller via UDP ports 10040 (Control) and 10041 (File).

Use carefully in production environments. High-speed commands control real robot motion!
