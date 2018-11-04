import time
from rodent_control.external import gertbot as gb


SERIAL_PORT = 0
BOARD = 3
CHANNEL = 0
SOLENOID_PIN = 6

DEBUG = False

# Connect to gertbot
try:
    gb.open_uart(SERIAL_PORT)
except Exception as e:
    print("***WARNING - COULD NOT CONNECT TO GERTBOT!***")
    print(str(e))
    DEBUG = True


def water_reward(delay=500, speed=150, distance=25):
    """Motor control to dispense rewards"""
    if DEBUG:
        # if hardware not connected, run dummy reward
        print("very best debug reward")
        return

    solenoid_open_delay = 200  # ms solenoid remains open for

    # Setup channel for stepper motor
    gb.set_mode(BOARD, CHANNEL, gb.MODE_STEPG_OFF)
    gb.set_pin_mode(BOARD, SOLENOID_PIN, gb.PIN_OUTPUT)

    # Water reward logic
    # First, move motor in
    gb.move_stepper(BOARD, CHANNEL, -distance)
    time.sleep(distance/speed) # Account for movement forward

    # Open solenoid
    pin_state = (1<<SOLENOID_PIN)  
    gb.set_output_pin_state(BOARD, pin_state)  # Set pin to high
    time.sleep(solenoid_open_delay)  # wait for enough water to drip
    pin_state &= ~(1<<SOLENOID_PIN) 
    gb.set_output_pin_state(BOARD, pin_state)  # set pin to low

    # Wait!
    time.sleep(delay/1000)  # Delay conversion from msec to sec

    # Move stepper back
    gb.move_stepper(BOARD, CHANNEL, distance-5)  # Less backward steps so spout ends up in same place
