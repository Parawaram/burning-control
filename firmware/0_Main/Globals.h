#pragma once
#include <Arduino.h>

constexpr uint8_t PIN_RELAY1 = 22;
constexpr uint8_t PIN_RELAY2 = 23;
constexpr uint8_t PIN_BUTTON = 2;

struct VoltageSensorData {
  float current;   // A
  float voltage;   // V
  float power;     // W
  bool  isAvailable;
};

struct TemperatureSensorData {
  float temperature;  // C
  float humidity;     // %
  bool  isAvailable;
};

struct Telemetry {
  uint32_t ts;        // millis()
  VoltageSensorData voltageSensorV3;
  VoltageSensorData voltageSensorV5;
  VoltageSensorData voltageSensorV5PiBrain;
  VoltageSensorData voltageSensorV24;
  TemperatureSensorData temperatureSensor1;
  TemperatureSensorData temperatureSensor2;
  bool  relay1;
  bool  relay2;
  bool  button;
};
extern Telemetry data;

void initSensors();
void pollSensors();

void initActuators();
void updateActuators();
void setRelay(uint8_t pin, bool state);

bool buttonPressed();
