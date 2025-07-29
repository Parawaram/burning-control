#include "Globals.h"

static bool stateRelay1 = false;
static bool stateRelay2 = false;
static uint32_t lastChange1 = 0;
static uint32_t lastChange2 = 0;

void initActuators() {
  pinMode(PIN_RELAY1, OUTPUT);
  pinMode(PIN_RELAY2, OUTPUT);
  digitalWrite(PIN_RELAY1, LOW);
  digitalWrite(PIN_RELAY2, LOW);
}

void setRelay(uint8_t pin, bool state) {
  uint32_t now = millis();
  uint32_t debounce = 20;
  if (pin == PIN_RELAY1) {
    if (state != stateRelay1 && now - lastChange1 >= debounce) {
      digitalWrite(pin, state ? HIGH : LOW);
      stateRelay1 = state;
      lastChange1 = now;
    }
  } else if (pin == PIN_RELAY2) {
    if (state != stateRelay2 && now - lastChange2 >= debounce) {
      digitalWrite(pin, state ? HIGH : LOW);
      stateRelay2 = state;
      lastChange2 = now;
    }
  }
}

void updateActuators() {
  if (data.voltageSensorV24.current > 2.0f) {
    setRelay(PIN_RELAY1, false);
  }
  data.relay1 = digitalRead(PIN_RELAY1);
  data.relay2 = digitalRead(PIN_RELAY2);
}
