#pragma once
#include <Arduino.h>

constexpr uint8_t PIN_RELAY1 = 22;
constexpr uint8_t PIN_RELAY2 = 23;
constexpr uint8_t PIN_BUTTON = 2;

struct Telemetry {
  uint32_t ts;        // millis()
  float voltage;      // V
  float current;      // A
  float power;        // W
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
