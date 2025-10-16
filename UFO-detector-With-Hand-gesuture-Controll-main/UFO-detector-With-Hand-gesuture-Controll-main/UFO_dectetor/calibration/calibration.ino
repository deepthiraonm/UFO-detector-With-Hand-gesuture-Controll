#include <Servo.h>

Servo myServo; // Create a servo object

void setup() {
  myServo.attach(12); // Attach the servo to pin 12
  myServo.write(90); // Set the servo to 0 degrees (initial position)
}

void loop() {
  // Nothing to do here, the servo remains at 0 degrees
}
