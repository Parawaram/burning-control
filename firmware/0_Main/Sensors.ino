#include "Globals.h"
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219(0x40);

void initSensors() {
  ina219.begin();
}

void pollSensors() {
  data.ts = millis();
  data.voltage = ina219.getBusVoltage_V();
  data.current = ina219.getCurrent_mA() / 1000.0f;
  data.power = data.voltage * data.current;
  data.button = buttonPressed();
  data.relay1 = digitalRead(PIN_RELAY1);
  data.relay2 = digitalRead(PIN_RELAY2);
}
