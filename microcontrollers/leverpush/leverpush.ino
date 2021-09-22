#include <Servo.h>
#define SERVO_PIN 9
#define BACK_SENSOR_PIN 2
#define FRONT_SENSOR_PIN 3
#define POS_LOCKED 20
#define POS_UNLOCKED 90

Servo leverServo;

int BackSensorState = 0;   // State of IR sensor at original lever position
int FrontSensorState = 0;  // State of IR sensor at the forward lever position

void setup() {
    pinMode(BACK_SENSOR_PIN, INPUT_PULLUP);
    pinMode(FRONT_SENSOR_PIN, INPUT_PULLUP);

    Serial.begin(9600);

    leverServo.attach(SERVO_PIN, 1000, 2000);
    leverServo.write(POS_LOCKED);

}

void loop() {
    // Check for messages on the serial console.
    if (Serial.available() > 0) {
        char msg = Serial.read();
        if (msg == 'T')
            test();
        if (msg == 'L')
            leverLock();
        if (msg == 'U')
            leverUnlock();
    }

    // Read sensor states and write to serial if there's a response.
    BackSensorState = digitalRead(BACK_SENSOR_PIN);
    FrontSensorState = digitalRead(FRONT_SENSOR_PIN);

    // When the lever is moved forward, the front IR sensor is broken and the back one is re-established.
    if (BackSensorState == HIGH && FrontSensorState == LOW)
        Serial.println("R");

    delay(50); // allow buffer to fill
}

void test() {
    // Cycle the servos and blink the indicator light
    digitalWrite(LED_BUILTIN, HIGH);
    leverUnlock();
    digitalWrite(LED_BUILTIN, LOW);
    leverLock();
    digitalWrite(LED_BUILTIN, HIGH);
    leverUnlock();
    digitalWrite(LED_BUILTIN, LOW);
    leverLock();
}

void leverLock() {
    leverServo.write(POS_LOCKED);
    delay(500); // Servo movement epoch
}

void leverUnlock() {
    leverServo.write(POS_UNLOCKED);
    delay(500); // Servo movement epoch
}
