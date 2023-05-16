#include <Servo.h>
#define SERVO_PIN 9
#define BUTTON_PIN 11
#define SOL_PIN 4

Servo spoutServo;

int buttonState = 0;
bool dispensing = false;

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SOL_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  Serial.begin(9600);
  spoutServo.attach(SERVO_PIN, 1000, 2000);
  spoutServo.write(50);
}

void loop() {
  buttonState = digitalRead(BUTTON_PIN);
  if (buttonState == 1) {
    if (dispensing == false) {
      dispensing = true;
      dispenseReward(false);
      dispensing = false;
    }
  }
  if (Serial.available() > 0) {
    char state = Serial.read();
    if (state == 'T') {
      dispenseReward(true);
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
      spoutServo.write(20);
      delay(500);
    }
    if (state == 'P' || state == 'p') {
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(SOL_PIN, HIGH);
      Serial.println("SOL ON");
    }
    if (state == 'O' || state == 'o') {
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(SOL_PIN, LOW);
      Serial.println("SOL OFF");
    }
  }
  delay(50); // allow buffer to fill
}

void dispenseReward(bool retract) {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("LED ON");
  spoutServo.write(150);
  delay(500); // spout movement epoch

  digitalWrite(SOL_PIN, HIGH); // reward dispension
  delay(15);
  digitalWrite(SOL_PIN, LOW);

  if (retract) {
    delay(1400); // delay for mouse to drink
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("LED OFF");
    spoutServo.write(50);
    delay(500); // spout movement epoch
  }
}
