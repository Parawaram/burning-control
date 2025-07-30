#include "Globals.h"
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_AHTX0.h>

Telemetry data;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);

  initSensors();
  initActuators();
}

static void printVoltageSensor(const char *name, const VoltageSensorData &s, bool last=false) {
  Serial.print('"');
  Serial.print(name);
  Serial.print("\":{");
  Serial.print("\"current\":"); Serial.print(s.isAvailable ? s.current : 0, 3);
  Serial.print(",\"voltage\":"); Serial.print(s.isAvailable ? s.voltage : 0, 3);
  Serial.print(",\"power\":"); Serial.print(s.isAvailable ? s.power : 0, 3);
  Serial.print(",\"isAvailable\":"); Serial.print(s.isAvailable ? "true" : "false");
  Serial.print('}');
  if (!last) Serial.print(',');
}

static void printTempSensor(const char *name, const TemperatureSensorData &s, bool last=false) {
  Serial.print('"');
  Serial.print(name);
  Serial.print("\":{");
  Serial.print("\"temperature\":"); Serial.print(s.isAvailable ? s.temperature : 0, 1);
  Serial.print(",\"humidity\":"); Serial.print(s.isAvailable ? s.humidity : 0, 1);
  Serial.print(",\"isAvailable\":"); Serial.print(s.isAvailable ? "true" : "false");
  Serial.print('}');
  if (!last) Serial.print(',');
}

void sendJson() {
  Serial.print('{');
  printVoltageSensor("voltageSensorV3", data.voltageSensorV3);
  printVoltageSensor("voltageSensorV5", data.voltageSensorV5);
  printVoltageSensor("voltageSensorV24", data.voltageSensorV24);
  printTempSensor("temperatureSensor1", data.temperatureSensor1);
  printTempSensor("temperatureSensor2", data.temperatureSensor2, true);
  Serial.print('}');
  Serial.print('\n');
}

void loop() {
  static uint32_t lastPoll = 0;
  uint32_t now = millis();

  if (now - lastPoll >= 100) {
    lastPoll = now;
    pollSensors();
    updateActuators();
    sendJson();
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
}
