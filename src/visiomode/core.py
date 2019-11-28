import time
import pigpio
#from adafruit_motor import stepper as stp

#try:
#    import adafruit_motorkit as mk
#    DEBUG = False
#except NotImplementedError:
#    print("Could not connect to motor board - ")
#    DEBUG = True

try:
    from gpiozero import OutputDevice as PinOut
except Exception as e:
    print("Could not load RPi GPIO library - " + str(e))


SOLENOID_PIN = 25  # BCM numbering
SERVO_PIN = 19
SERVO_START = 1200

pi = pigpio.pi()
pi.set_servo_pulsewidth(SERVO_PIN, SERVO_START)

#if not DEBUG:
#    motor_kit = mk.MotorKit()


#def water_reward(delay=500, speed=150, distance=25):
def water_reward(delay=500, servo_away=SERVO_START, servo_reward=1800):
    """Motor control to dispense rewards"""
    #if DEBUG:
     #   # if hardware not connected, run dummy reward
     #   print("very best debug reward")
     #   return

    solenoid_open_delay = 150  # ms solenoid remains open for
    #motor_movt_delay = distance / speed  # Amount of time motor takes to move
    #reward_delay = delay - (solenoid_open_delay - motor_movt_delay)
    reward_delay = delay - solenoid_open_delay

    # Water reward logic
    # First, move motor in
    #for i in range(distance):
    #    motor_kit.stepper1.onestep(direction=stp.FORWARD)
    #time.sleep(motor_movt_delay)  # Account for movement forward
    pi.set_servo_pulsewidth(SERVO_PIN, servo_reward)

    # Open solenoid - plugged into RPi port!
    solenoid = PinOut(SOLENOID_PIN)
    solenoid.on()
    time.sleep(solenoid_open_delay / 1000)  # wait for enough water to drip
    solenoid.off()

    # Wait!
    time.sleep(reward_delay / 1000)  # Delay conversion from msec to sec

    # Move stepper back
    #for i in range(distance - 10):  # Less backward steps - spout ends up in same place
    #    motor_kit.stepper1.onestep(direction=stp.BACKWARD)
    pi.set_servo_pulsewidth(SERVO_PIN, servo_away)

    #motor_kit.stepper1.release()  # release motor to save power / avoid overheating
