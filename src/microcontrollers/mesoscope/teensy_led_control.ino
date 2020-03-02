/*
   LED strobing and camera trigger for mesoscope
   Copyright (c) 2019 Constantinos Eleftheriou (Constantinos.Eleftheriou@ed.ac.uk)

   This code is released under the MIT licence (https://opensource.org/licenses/MIT)

   Permission is hereby granted, free of charge, to any person obtaining a copy 
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights 
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
   of the Software, and to permit persons to whom the Software is furnished to do 
   so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all 
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
   INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

const int led1Pin = 16;
const int led2Pin = 26;
const int camPin = 6;
const int acqDelay = 10;  // this is half the required frequency (50Hz = 20ms)

void setup() {
  // init digital pins as output
  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  pinMode(camPin, OUTPUT);
}

void loop() {
  // LED 1 cycle
  digitalWrite(led1Pin, HIGH);
  delay(acqDelay);
  digitalWrite(camPin, HIGH);
  delay(acqDelay);
  digitalWrite(camPin, LOW);
  digitalWrite(led1Pin, LOW);

  // LED 2 cycle
  digitalWrite(led2Pin, HIGH);
  delay(acqDelay);
  digitalWrite(camPin, HIGH);
  delay(acqDelay);
  digitalWrite(camPin, LOW);
  digitalWrite(led2Pin, LOW);
}
