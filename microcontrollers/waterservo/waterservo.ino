#include <Servo.h>
#define SERVO_PIN 9
#define PUMP_PIN 3
#define SOL_PIN 2

Servo spoutServo;

int servoAngle = 5;

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(SOL_PIN, OUTPUT);
  Serial.begin(9600);
  spoutServo.attach(SERVO_PIN, 1000, 2000);
  spoutServo.write(70);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char state = Serial.read();
    if (state == 'T') {
        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("LED ON");
        spoutServo.write(150);
        delay(500);

        digitalWrite(PUMP_PIN, HIGH);
        digitalWrite(SOL_PIN, HIGH);
        delay(100);
        digitalWrite(PUMP_PIN, LOW);
        digitalWrite(SOL_PIN, LOW);
        delay(700);

        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("LED OFF");
        spoutServo.write(70);
        delay(500);
    }
    if (state == 'H' || state == 'h') {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED ON");
      spoutServo.write(150);
      delay(500);
    }
    if (state == 'L' || state == 'l') {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED OFF");
      spoutServo.write(70);
      delay(500);
    }
    if (state == 'P' || state == 'p') {
      digitalWrite(PUMP_PIN, HIGH);
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(SOL_PIN, HIGH);
      Serial.println("PUMP ON");
    }
    if (state == 'O' || state == 'o') {
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(PUMP_PIN, LOW);
      digitalWrite(SOL_PIN, LOW);
      Serial.println("PUMP OFF");
    }
  }
  delay(50); // allow buffer to fill
}
