import time
from rodent_control.external import gertbot as gb

try:
    from gpiozero import OutputDevice
except Exception as e:
    print("Could not load RPi GPIO library - " + str(e))


SERIAL_PORT = 0
BOARD = 3
CHANNEL = 0
SOLENOID_PIN = 16  # Plugged in Rpi, BCM numbering

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
    motor_movt_delay = distance / speed  # Amount of time motor takes to move
    reward_delay = delay - (solenoid_open_delay - motor_movt_delay)

    # Setup channel for stepper motor
    gb.set_mode(BOARD, CHANNEL, gb.MODE_STEPG_OFF)
    gb.set_pin_mode(BOARD, SOLENOID_PIN, gb.PIN_OUTPUT)

    # Water reward logic
    # First, move motor in
    gb.move_stepper(BOARD, CHANNEL, -distance)
    time.sleep(motor_movt_delay) # Account for movement forward

    # Open solenoid - plugged into RPi port!
    solenoid = OutputDevice(SOLENOID_PIN)
    solenoid.on()
    time.sleep(solenoid_open_delay / 1000)  # wait for enough water to drip
    solenoid.off()

    # Wait!
    time.sleep(reward_delay / 1000)  # Delay conversion from msec to sec

    # Move stepper back
    gb.move_stepper(BOARD, CHANNEL, distance-5)  # Less backward steps so spout ends up in same place
