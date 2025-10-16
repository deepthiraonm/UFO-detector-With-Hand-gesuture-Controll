#include <Servo.h>

// Defines Trigger and Echo pins of the Ultrasonic Sensor
const int trigPin = 10;
const int echoPin = 11;
const int buzzerPin = 9; // Defines the pin for the buzzer

// Defines RGB LED pins
const int redPin = 3;
const int greenPin = 4;
const int bluePin = 5;

// Variables for the duration and the distance
long duration;
int distance;
Servo myServo; // Creates a servo object for controlling the servo motor

const int minRange = 10; // Minimum range in cm to consider an obstacle
const int maxRange = 40 ; // Maximum range in cm to consider an obstacle

void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  pinMode(buzzerPin, OUTPUT); // Sets the buzzerPin as an Output

  // Set RGB LED pins as OUTPUT
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  Serial.begin(9600);
  myServo.attach(12); // Defines on which pin the servo motor is attached

  // Initialize RGB LED to OFF
  setColor(0, 0, 0); // All colors off
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "STOP") {
      // Stop the servo motor
      myServo.detach();
      return;
    }

    // Otherwise, assume command is an angle value
    int angle = command.toInt();
    
    if (angle >= 0 && angle <= 180) {
      myServo.attach(12); // Reattach servo if detached
      myServo.write(angle);
    }
  }

  distance = calculateDistance(); // Calls a function for calculating the distance measured by the Ultrasonic sensor

  if (distance >= minRange && distance <= maxRange) {
    // Control the buzzer based on the distance
    controlBuzzer(distance);

    // Control the RGB LED based on the distance
    setColor(distance);
  } else {
    // Control the buzzer based on the distance
    controlBuzzer(distance);

    // Control the RGB LED based on the distance
    setColor(distance);
  }
}

// Function for calculating the distance measured by the Ultrasonic sensor
int calculateDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Sets the trigPin on HIGH state for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH); // Reads the echoPin, returns the sound wave travel time in microseconds
  distance = duration * 0.034 / 2;   // Calculating the distance

  return distance;
}

// Function to control the buzzer based on the distance
void controlBuzzer(int distance) {
  int frequency;
  int buzzerDelay;

  if (distance <= 10) {
    frequency = 2000; // High frequency sound for very close objects
    buzzerDelay = 50; // Short delay for very close objects
  } else if (distance <= 20) {
    frequency = 1500; // Medium high frequency sound
    buzzerDelay = 100; // Medium short delay
  } else if (distance <= 30) {
    frequency = 1000; // Medium frequency sound
    buzzerDelay = 150; // Medium delay
  } else if (distance <= 40) {
    frequency = 500; // Low frequency sound
    buzzerDelay = 200; // Long delay
  } else {
    noTone(buzzerPin); // Turn off the buzzer for distances greater than 40 cm
    return;
  }

  tone(buzzerPin, frequency);
  delay(buzzerDelay);
  noTone(buzzerPin); // Turn off the buzzer briefly to create a non-continuous sound
}

// Function to control RGB LED color
void setColor(int red, int green, int blue) {
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}

void setColor(int distance) {
  if (distance <= 10) {
    setColor(255, 0, 0); // Red
  } else if (distance <= 20) {
    setColor(139, 0, 0); // Scarlet
  } else if (distance <= 30) {
    setColor(255, 165, 0); // Orange
  } else if (distance <= 40) {
    setColor(255, 255, 0); // Yellow
  } else {
    setColor(0, 255, 0); // Green
  }
}