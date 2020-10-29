/*
Water reward controller.
Works for servos and
*/
#define OUT_PIN 4
#define DELAY 35

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(OUT_PIN, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 'T') {
            digitalWrite(LED_BUILTIN, HIGH);
            Serial.println("Dispensing...");
            digitalWrite(OUT_PIN, HIGH);
            delay(DELAY);
            digitalWrite(OUT_PIN, LOW);
            digitalWrite(LED_BUILTIN, LOW);
        }
        if (cmd == 'P' || cmd == 'p') {
          digitalWrite(OUT_PIN, HIGH);
          digitalWrite(LED_BUILTIN, HIGH);
          digitalWrite(OUT_PIN, HIGH);
          Serial.println("PUMP ON");
        }
        if (cmd == 'O' || cmd == 'o') {
          digitalWrite(LED_BUILTIN, LOW);
          digitalWrite(OUT_PIN, LOW);
          Serial.println("PUMP OFF");
        }
    }
}
