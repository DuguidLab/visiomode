import time
from rodent_control.external import gertbot as gb


SERIAL_PORT = 0
BOARD = 3
CHANNEL = 0


def water_reward(delay=500, speed=150, distance=100):
    """Motor control to dispense rewards"""

    # Connect to gertbot
    gb.open_uart(SERIAL_PORT)

    # Setup channel for stepper motor
    gb.set_mode(BOARD, CHANNEL, gb.MODE_STEPG_OFF)

    # Water reward logic
    gb.move_stepper(BOARD, CHANNEL, distance)
    time.sleep(delay/1000)  # Delay conversion from msec to sec
    gb.move_stepper(BOARD, CHANNEL, -distance)
