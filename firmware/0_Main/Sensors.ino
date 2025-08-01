#include "Globals.h"

Adafruit_INA219 sensorV3(0x40);       // 3.3V
Adafruit_INA219 sensorV5(0x41);       // 5V
Adafruit_INA219 sensorV5PiBrain(0x44); // 5V Pi Brain
Adafruit_INA219 sensorV24(0x45);      // 24V

static bool v3_ok = false;
static bool v5_ok = false;
static bool v5pb_ok = false;
static bool v24_ok = false;

Adafruit_AHTX0 aht1; // address 0x38
Adafruit_AHTX0 aht2; // address 0x39

static bool aht1_ok = false;
static bool aht2_ok = false;


static bool startIna(Adafruit_INA219 &sensor) {
  for (int i = 0; i < 3; ++i) {
    if (sensor.begin()) return true;
    delay(10);
  }
  return false;
}

static void ensureInaStarted(Adafruit_INA219 &sensor, bool &okFlag) {
  if (!okFlag) {
    okFlag = startIna(sensor);
  }
}

static void readIna(Adafruit_INA219 &sensor, bool &okFlag, VoltageSensorData &out) {
  ensureInaStarted(sensor, okFlag);
  if (!okFlag) {
    out.current = 0.0f;
    out.voltage = 0.0f;
    out.power = 0.0f;
    out.isAvailable = false;
    return;
  }
  float v = sensor.getBusVoltage_V();
  float i = sensor.getCurrent_mA() / 1000.0f;
  bool ok = !isnan(v) && !isinf(v) && !isnan(i) && !isinf(i);
  if (!ok) {
    okFlag = false;
    out.voltage = 0.0f;
    out.current = 0.0f;
    out.power = 0.0f;
    out.isAvailable = false;
    return;
  }
  float p = v * i;
  if (isnan(p) || isinf(p)) {
    p = 0.0f;
  }
  out.voltage = v;
  out.current = i;
  out.power = p;
  out.isAvailable = true;
}

static void readAHT(Adafruit_AHTX0 &sensor, bool okFlag, TemperatureSensorData &out) {
  if (!okFlag) {
    out.temperature = 0.0f;
    out.humidity = 0.0f;
    out.isAvailable = false;
    return;
  }
  sensors_event_t hum, temp;
  sensor.getEvent(&hum, &temp);
  float t = temp.temperature;
  float h = hum.relative_humidity;
  bool ok = !isnan(t) && !isinf(t) && !isnan(h) && !isinf(h);
  if (!ok) {
    t = 0.0f;
    h = 0.0f;
  }
  out.temperature = t;
  out.humidity = h;
  out.isAvailable = ok;
}

void initSensors() {
  v3_ok = startIna(sensorV3);
  v5_ok = startIna(sensorV5);
  v5pb_ok = startIna(sensorV5PiBrain);
  v24_ok = startIna(sensorV24);
  // pass explicit Wire instance and sensor ID to avoid implicit int conversion
  aht1_ok = aht1.begin(&Wire, -1, 0x38);
  aht2_ok = aht2.begin(&Wire, -1, 0x39);
}

void pollSensors() {
  data.ts = millis();
  readIna(sensorV3, v3_ok, data.voltageSensorV3);
  readIna(sensorV5, v5_ok, data.voltageSensorV5);
  readIna(sensorV5PiBrain, v5pb_ok, data.voltageSensorV5PiBrain);
  readIna(sensorV24, v24_ok, data.voltageSensorV24);
  readAHT(aht1, aht1_ok, data.temperatureSensor1);
  readAHT(aht2, aht2_ok, data.temperatureSensor2);
  data.button = buttonPressed();
  data.relay1 = digitalRead(PIN_RELAY1);
  data.relay2 = digitalRead(PIN_RELAY2);
}
