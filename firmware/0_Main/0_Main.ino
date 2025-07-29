#include "Globals.h"
#include <Wire.h>

Telemetry data;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);

  initSensors();
  initActuators();
}

void sendJson() {
  Serial.print('{');
  Serial.print("\"ts\":"); Serial.print(data.ts);
  Serial.print(",\"U\":"); Serial.print(data.voltage, 2);
  Serial.print(",\"I\":"); Serial.print(data.current, 3);
  Serial.print(",\"P\":"); Serial.print(data.power, 2);
  Serial.print(",\"R\":["); Serial.print(data.relay1); Serial.print(','); Serial.print(data.relay2); Serial.print(']');
  Serial.print(",\"B\":"); Serial.print(data.button);
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
