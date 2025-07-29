#include "Globals.h"

bool buttonPressed() {
  static bool lastReading = HIGH;
  static bool lastStable = HIGH;
  static uint32_t lastDebounce = 0;
  const uint32_t debounceDelay = 30;

  bool reading = digitalRead(PIN_BUTTON);
  if (reading != lastReading) {
    lastDebounce = millis();
    lastReading = reading;
  }
  if (millis() - lastDebounce >= debounceDelay) {
    if (reading != lastStable) {
      lastStable = reading;
      if (lastStable == LOW) {
        return true;
      }
    }
  }
  return false;
}
