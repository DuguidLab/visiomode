void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char state = Serial.read();
    if (state == 'H' || state == 'h') {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED ON");
    }
    if (state == 'L' || state == 'l') {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED OFF");
    }
  }
  delay(50);
}
