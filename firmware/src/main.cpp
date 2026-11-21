#include <Arduino.h>

// Motor derecho
#define fw_right_pin 5
#define bw_right_pin 18
// Motor izquierdo
#define fw_left_pin 19
#define bw_left_pin 21
// Enable (velocidad) L298N
#define speedR_pin 25
#define speedL_pin 26
// HC-SR04 (ECHO debe pasar por divisor de voltaje 5V -> 3.3V)
#define trig_pin 13
#define echo_pin 14

const float OBSTACLE_DIST_CM = 10.0;
const unsigned long SENSOR_PERIOD_MS = 60;

enum Cmd { STOP, FORWARD, BACKWARD, LEFT, RIGHT };
Cmd current = STOP;

String rxBuffer = "";
unsigned long lastSensor = 0;

void setMotors(bool rf, bool rb, bool lf, bool lb) {
  digitalWrite(fw_right_pin, rf);
  digitalWrite(bw_right_pin, rb);
  digitalWrite(fw_left_pin, lf);
  digitalWrite(bw_left_pin, lb);
}

void applyCmd(Cmd c) {
  current = c;
  bool en = (c != STOP);
  digitalWrite(speedR_pin, en);
  digitalWrite(speedL_pin, en);
  switch (c) {
    case FORWARD:  setMotors(1, 0, 1, 0); break;
    case BACKWARD: setMotors(0, 1, 0, 1); break;
    case LEFT:     setMotors(1, 0, 0, 1); break;  // gira sobre su eje
    case RIGHT:    setMotors(0, 1, 1, 0); break;
    default:       setMotors(0, 0, 0, 0); break;
  }
}

// Distancia en cm, o -1 si no hay eco válido
float readUltrasound() {
  digitalWrite(trig_pin, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin, LOW);
  unsigned long duration = pulseIn(echo_pin, HIGH, 25000UL);
  if (duration == 0) return -1;
  return duration * 0.0343 / 2.0;
}

void handleCommand(String s) {
  s.trim();
  s.toLowerCase();
  if (s == "forward")       applyCmd(FORWARD);
  else if (s == "backward") applyCmd(BACKWARD);
  else if (s == "left")     applyCmd(LEFT);
  else if (s == "right")    applyCmd(RIGHT);
  else if (s == "stop")     applyCmd(STOP);
  else { Serial.print("ERR:"); Serial.println(s); return; }
  Serial.print("OK:"); Serial.println(s);
}

void setup() {
  Serial.begin(115200);
  pinMode(fw_right_pin, OUTPUT);
  pinMode(bw_right_pin, OUTPUT);
  pinMode(fw_left_pin, OUTPUT);
  pinMode(bw_left_pin, OUTPUT);
  pinMode(speedR_pin, OUTPUT);
  pinMode(speedL_pin, OUTPUT);
  pinMode(trig_pin, OUTPUT);
  pinMode(echo_pin, INPUT);
  applyCmd(STOP);
}

void loop() {
  // 1) Comandos desde ROS
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { handleCommand(rxBuffer); rxBuffer = ""; }
    else if (c != '\r') rxBuffer += c;
  }

  // 2) Sensor + parada automática
  if (millis() - lastSensor >= SENSOR_PERIOD_MS) {
    lastSensor = millis();
    float d = readUltrasound();
    Serial.print("D:"); Serial.println(d);
    if (current == FORWARD && d > 0 && d < OBSTACLE_DIST_CM) {
      applyCmd(STOP);
      Serial.println("OBSTACLE");
    }
  }
}
