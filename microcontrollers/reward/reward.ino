#include <Servo.h>
#define SERVO_PIN 9

Servo spoutServo;

int servoAngle = 5;

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  spoutServo.attach(SERVO_PIN, 1000, 2000);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char state = Serial.read();
    if (state == 'T') {
        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("LED ON");
        spoutServo.write(170);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("LED OFF");
        spoutServo.write(10);
        delay(500);
    }
    if (state == 'H' || state == 'h') {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED ON");
      spoutServo.write(170);
      delay(500);
    }
    if (state == 'L' || state == 'l') {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED OFF");
      spoutServo.write(10);
      delay(500);
    }
  }
  delay(50); // allow buffer to fill
}
