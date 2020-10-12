/*
Water reward controller.
Works for servos and 
*/
#define OUT_PIN 3
#define DELAY 100

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinmode(OUT_PIN, OUTPUT);
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
    }
}