#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <ThingSpeak.h>
#include <U8g2lib.h>
#include <arduino-timer.h>
#include <Adafruit_LIS3DH.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_NeoPixel.h>
#include <math.h>

static const uint8_t PIN_OLED_SDA = 8;
static const uint8_t PIN_OLED_SCL = 9;
static const uint8_t PIN_TOUCH_NEXT = 4;
static const uint8_t PIN_CLOCK_BUTTON = 7;

// Dedicated LTC2990 sensor bus (ideal general-purpose pins on ESP32-S3)
static const uint8_t PIN_LTC_SDA = 17;
static const uint8_t PIN_LTC_SCL = 18;

static const uint8_t LTC_ADDR_GND_GND = 0x4C;  // A1=GND, A0=GND
static const uint8_t LTC_ADDR_SECONDARY = 0x4F;  // A1=VCC, A0=VCC
static const uint32_t OLED_I2C_CLOCK_HZ = 100000;
static const uint32_t LTC_I2C_CLOCK_HZ = 50000;
static const uint16_t I2C_TIMEOUT_MS = 20;
static const uint32_t THINGSPEAK_PUBLISH_MS = 15000;
static const uint32_t THINGSPEAK_CONTROL_POLL_MS = 15000;

static const char *WIFI_SSID = "832";
static const char *WIFI_PASSWORD = "83221266";
static const unsigned long THINGSPEAK_CHANNEL_ID = 3401402;
static const char *THINGSPEAK_WRITE_API_KEY = "XB3I5S8PC8G17397";
static const char *THINGSPEAK_READ_API_KEY = "N6QVYK9PIQPVMYBN";
static const uint8_t THINGSPEAK_LED_FIELD = 8;

static const uint8_t NEOPIXEL_COUNT = 1;
static const uint8_t NEOPIXEL_BRIGHTNESS = 24;

// BB-2020BGR-TRB is an APA102-compatible 5V RGB LED with clock+data timing.
static const uint8_t PIN_RING_DATA = 11;
static const uint8_t PIN_RING_CLOCK = 12;
static const uint8_t PIN_ARRAY_DATA = 5;
static const uint8_t PIN_ARRAY_CLOCK = 6;
static const uint16_t LED_RING_COUNT = 50;
static const uint8_t LED_RING_BRIGHTNESS = 24;  // 1..31 (datasheet global brightness bits)
// Zero selects the fastest software-driven clock this implementation can produce.
// The GPIO bit-bang path cannot guarantee a measured 11 MHz clock.
static const uint16_t APA102_CLOCK_HALF_PERIOD_US[] = {500, 100, 20, 5, 2, 0};
static const uint8_t APA102_CLOCK_MODE_COUNT = sizeof(APA102_CLOCK_HALF_PERIOD_US) / sizeof(APA102_CLOCK_HALF_PERIOD_US[0]);

static const uint8_t PIN_HEATER_RELAY = 13;

U8G2_SH1106_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
TwoWire ltcBus(1);
WiFiClient thingSpeakClient;
auto appTimer = timer_create_default();
Adafruit_NeoPixel statusPixel(NEOPIXEL_COUNT, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);

Adafruit_LIS3DH lis3dh(&ltcBus);
Adafruit_MPU6050 mpu6050;

static const uint8_t LTC_REG_CONTROL = 0x01;
static const uint8_t LTC_REG_TRIGGER = 0x02;
static const uint8_t LTC_REG_TINT_MSB = 0x04;
static const uint8_t LTC_REG_V1_MSB = 0x06;
static const uint8_t LTC_REG_V2_MSB = 0x08;
static const uint8_t LTC_REG_V3_MSB = 0x0A;
static const uint8_t LTC_REG_V4_MSB = 0x0C;
static const uint8_t LTC_REG_VCC_MSB = 0x0E;

static const uint8_t LTC_CTRL_REPEATED_C = 0x1F;  // repeated + Celsius + enable all + V1..V4
static const float LTC_SINGLE_ENDED_LSB = 0.00030518f;
static const float LTC_TEMP_LSB = 0.0625f;

struct LtcSample {
  bool ok;
  uint8_t quality;
  float tempC;
  float vcc;
  float v1;
  float v2;
  float v3;
  float v4;
  float d1mv;
  float d2mv;
};

enum class LtcFailStage {
  None,
  Probe,
  ConfigCtrl,
  ConfigTrig,
  ReadAddr,
  ReadData,
};

struct LtcDiag {
  bool present;
  bool configured;
  uint32_t consecutiveFailCount;
  uint32_t recoverCount;
  uint32_t allZeroCount;
  uint32_t rangeFailCount;
  uint32_t shortFailCount;
  uint32_t probeFailCount;
  uint32_t configFailCount;
  uint32_t readFailCount;
  uint32_t okReadCount;
  LtcFailStage lastFailStage;
  uint8_t lastFailReg;
  uint8_t lastTxStatus;
  uint8_t lastRxCount;
};

struct BusScanInfo {
  uint8_t count;
  bool has4c;
  bool has4f;
  char list[28];
};

enum class AccelType {
  None,
  LIS3DH,
  MPU6050,
};

struct AccelSample {
  bool ok;
  float x;
  float y;
  float z;
};

enum class UiPage {
  BootScanOled,
  BootScanLtc,
  Summary,
  Detail4C,
  Detail4F,
  Accel,
  Status,
};

enum class LtcQuality : uint8_t {
  Good = 0,
  Missing,
  AllZero,
  ShortSuspect,
  OutOfRange,
  ReadFail,
};

static const uint32_t BOOT_PAGE_MS = 1500;
static const uint32_t RUN_PAGE_MS = 1200;
static const uint32_t SENSOR_REFRESH_MS = 500;  // 2 Hz live sensor/page update
static const uint32_t ACCEL_REFRESH_MS = 1000;
static const uint32_t TOUCH_DEBOUNCE_MS = 300;

UiPage currentPage = UiPage::BootScanOled;
bool bootSequenceDone = false;
BusScanInfo oledScan{};
BusScanInfo ltcScan{};
uint8_t oledDetectedAddr = 0;
LtcSample sample4c{};
LtcSample sample4f{};
LtcDiag diag4c{};
LtcDiag diag4f{};
AccelSample accelSample{};
AccelType accelType = AccelType::None;
char accelName[12] = "NONE";
uint32_t lastPageChangeMs = 0;
uint32_t lastSensorLogMs = 0;
uint32_t lastAddrDumpMs = 0;
uint32_t lastAccelReadMs = 0;
uint32_t lastThingSpeakPushMs = 0;
uint32_t lastThingSpeakControlPollMs = 0;
bool ltc4cPresent = false;
bool ltc4fPresent = false;
long ledCommand = 0;
bool heaterOn = false;

enum class RingPattern : uint8_t {
  Off = 0,
  Rainbow,
  MultiRainbow,
  RainbowPulse,
  Theater,
  Comet,
  Sparkle,
  TwinRainbow,
  ErrorFlash,
  White,
  Red,
  Green,
  Blue,
  Auto,
};

struct RingPixel {
  uint8_t b;
  uint8_t g;
  uint8_t r;
};

RingPixel ringLeds[LED_RING_COUNT];
RingPattern ringPattern = RingPattern::Auto;
uint32_t ringLastStepMs = 0;
uint32_t ringLastModeMs = 0;
uint8_t ringHue = 0;
uint16_t ringPos = 0;
uint8_t ringAutoIndex = 0;
uint8_t apa102ClockMode = 0;
bool clockButtonPressed = false;
uint32_t lastClockButtonEventMs = 0;

static inline void writeApa102BytePair(uint8_t v) {
  for (uint8_t i = 0; i < 8; ++i) {
    uint8_t level = (v & 0x80) ? HIGH : LOW;
    digitalWrite(PIN_RING_DATA, level);
    digitalWrite(PIN_ARRAY_DATA, level);
    delayMicroseconds(APA102_CLOCK_HALF_PERIOD_US[apa102ClockMode]);
    digitalWrite(PIN_RING_CLOCK, HIGH);
    digitalWrite(PIN_ARRAY_CLOCK, HIGH);
    delayMicroseconds(APA102_CLOCK_HALF_PERIOD_US[apa102ClockMode]);
    digitalWrite(PIN_RING_CLOCK, LOW);
    digitalWrite(PIN_ARRAY_CLOCK, LOW);
    v <<= 1;
  }
}

void ringBusShow() {
  // Start frame: 32 zero bits.
  writeApa102BytePair(0x00);
  writeApa102BytePair(0x00);
  writeApa102BytePair(0x00);
  writeApa102BytePair(0x00);

  uint8_t frameBrightness = LED_RING_BRIGHTNESS;
  if (frameBrightness < 1) {
    frameBrightness = 1;
  }
  if (frameBrightness > 31) {
    frameBrightness = 31;
  }
  uint8_t ledPrefix = static_cast<uint8_t>(0xE0 | frameBrightness);

  for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
    writeApa102BytePair(ledPrefix);
    writeApa102BytePair(ringLeds[i].b);
    writeApa102BytePair(ringLeds[i].g);
    writeApa102BytePair(ringLeds[i].r);
  }

  // End frame: enough clock pulses to latch all pixels.
  uint16_t endBytes = (LED_RING_COUNT + 15) / 16;
  for (uint16_t i = 0; i < endBytes; ++i) {
    writeApa102BytePair(0xFF);
  }
}

void ringSetAll(uint8_t r, uint8_t g, uint8_t b) {
  for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
    ringLeds[i].r = r;
    ringLeds[i].g = g;
    ringLeds[i].b = b;
  }
}

void ringWheel(uint8_t pos, uint8_t &r, uint8_t &g, uint8_t &b) {
  if (pos < 85) {
    r = static_cast<uint8_t>(pos * 3);
    g = static_cast<uint8_t>(255 - pos * 3);
    b = 0;
  } else if (pos < 170) {
    pos = static_cast<uint8_t>(pos - 85);
    r = static_cast<uint8_t>(255 - pos * 3);
    g = 0;
    b = static_cast<uint8_t>(pos * 3);
  } else {
    pos = static_cast<uint8_t>(pos - 170);
    r = 0;
    g = static_cast<uint8_t>(pos * 3);
    b = static_cast<uint8_t>(255 - pos * 3);
  }
}

void setRingPattern(RingPattern p) {
  ringPattern = p;
  ringPos = 0;
  if (p == RingPattern::Off) {
    ringSetAll(0, 0, 0);
    ringBusShow();
  }
  Serial.printf("[RING] pattern=%u\n", static_cast<unsigned>(p));
}

void updateLedRingPattern() {
  uint32_t now = millis();
  if ((now - ringLastStepMs) < 20) {
    return;
  }
  ringLastStepMs = now;

  RingPattern active = ringPattern;
  bool sensorDataError = !sample4c.ok || !sample4f.ok;
  if (ringPattern == RingPattern::Auto) {
    if ((now - ringLastModeMs) > 5000) {
      ringLastModeMs = now;
      ringAutoIndex = (ringAutoIndex + 1) % 9;
    }
    static const RingPattern kAutoSeq[9] = {
        RingPattern::MultiRainbow, RingPattern::Comet, RingPattern::Theater,
        RingPattern::Sparkle, RingPattern::Rainbow, RingPattern::RainbowPulse,
        RingPattern::TwinRainbow, RingPattern::MultiRainbow, RingPattern::Comet};
    active = kAutoSeq[ringAutoIndex];
  }

  switch (active) {
    case RingPattern::Off:
      ringSetAll(0, 0, 0);
      break;
    case RingPattern::Rainbow: {
      for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
        uint8_t r = 0;
        uint8_t g = 0;
        uint8_t b = 0;
        ringWheel(static_cast<uint8_t>(ringHue + (i * 256 / LED_RING_COUNT)), r, g, b);
        ringLeds[i].r = r;
        ringLeds[i].g = g;
        ringLeds[i].b = b;
      }
      ringHue++;
      break;
    }
    case RingPattern::MultiRainbow:
      for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
        uint8_t r = 0;
        uint8_t g = 0;
        uint8_t b = 0;
        ringWheel(static_cast<uint8_t>(ringHue + (i * 768 / LED_RING_COUNT)), r, g, b);
        ringLeds[i].r = r;
        ringLeds[i].g = g;
        ringLeds[i].b = b;
      }
      ringHue += 3;
      ringPos++;
      break;
    case RingPattern::RainbowPulse: {
      uint8_t pulse = static_cast<uint8_t>((ringHue & 0x7F) * 2);
      if (ringHue & 0x80) {
        pulse = static_cast<uint8_t>(255 - pulse);
      }
      for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
        uint8_t r = 0;
        uint8_t g = 0;
        uint8_t b = 0;
        ringWheel(static_cast<uint8_t>(ringHue + i * 256 / LED_RING_COUNT), r, g, b);
        ringLeds[i].r = static_cast<uint8_t>((r * pulse) / 255);
        ringLeds[i].g = static_cast<uint8_t>((g * pulse) / 255);
        ringLeds[i].b = static_cast<uint8_t>((b * pulse) / 255);
      }
      ringHue += 2;
      break;
    }
    case RingPattern::Theater:
      ringSetAll(0, 0, 0);
      for (uint16_t i = ringPos % 3; i < LED_RING_COUNT; i += 3) {
        uint8_t r = 0;
        uint8_t g = 0;
        uint8_t b = 0;
        ringWheel(ringHue, r, g, b);
        ringLeds[i].r = r;
        ringLeds[i].g = g;
        ringLeds[i].b = b;
      }
      ringHue += 2;
      ringPos++;
      break;
    case RingPattern::Comet:
      ringSetAll(0, 0, 0);
      for (uint8_t tail = 0; tail < 8; ++tail) {
        uint16_t index = static_cast<uint16_t>((ringPos + LED_RING_COUNT - tail) % LED_RING_COUNT);
        uint8_t r = 0;
        uint8_t g = 0;
        uint8_t b = 0;
        ringWheel(static_cast<uint8_t>(ringHue + tail * 10), r, g, b);
        uint8_t scale = static_cast<uint8_t>(255 - tail * 28);
        ringLeds[index].r = static_cast<uint8_t>((r * scale) / 255);
        ringLeds[index].g = static_cast<uint8_t>((g * scale) / 255);
        ringLeds[index].b = static_cast<uint8_t>((b * scale) / 255);
      }
      ringHue += 2;
      ringPos++;
      break;
    case RingPattern::Sparkle:
      ringSetAll(2, 2, 8);
      for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
        if (((i * 17 + ringHue) % 23) < 3) {
          uint8_t r = 0;
          uint8_t g = 0;
          uint8_t b = 0;
          ringWheel(static_cast<uint8_t>(ringHue + i * 7), r, g, b);
          ringLeds[i].r = r;
          ringLeds[i].g = g;
          ringLeds[i].b = b;
        }
      }
      ringHue += 4;
      break;
    case RingPattern::TwinRainbow:
      for (uint16_t i = 0; i < LED_RING_COUNT; ++i) {
        uint8_t r1 = 0;
        uint8_t g1 = 0;
        uint8_t b1 = 0;
        uint8_t r2 = 0;
        uint8_t g2 = 0;
        uint8_t b2 = 0;
        ringWheel(static_cast<uint8_t>(ringHue + i * 512 / LED_RING_COUNT), r1, g1, b1);
        ringWheel(static_cast<uint8_t>(ringHue + 128 - i * 512 / LED_RING_COUNT), r2, g2, b2);
        ringLeds[i].r = static_cast<uint8_t>((r1 + r2) / 2);
        ringLeds[i].g = static_cast<uint8_t>((g1 + g2) / 2);
        ringLeds[i].b = static_cast<uint8_t>((b1 + b2) / 2);
      }
      ringHue += 3;
      break;
    case RingPattern::ErrorFlash:
      if ((now / 250) % 2 == 0) {
        ringSetAll(255, 0, 0);
      } else {
        ringSetAll(255, 255, 255);
      }
      break;
    case RingPattern::White:
      ringSetAll(255, 255, 255);
      break;
    case RingPattern::Red:
      ringSetAll(255, 0, 0);
      break;
    case RingPattern::Green:
      ringSetAll(0, 255, 0);
      break;
    case RingPattern::Blue:
      ringSetAll(0, 0, 255);
      break;
    case RingPattern::Auto:
      // handled above
      break;
  }

  if (ringPattern == RingPattern::Auto && sensorDataError) {
    uint16_t warningPos = static_cast<uint16_t>((now / 80) % LED_RING_COUNT);
    for (uint8_t offset = 0; offset < 3; ++offset) {
      uint16_t index = static_cast<uint16_t>((warningPos + offset) % LED_RING_COUNT);
      if (offset == 1) {
        ringLeds[index].r = 255;
        ringLeds[index].g = 255;
        ringLeds[index].b = 255;
      } else {
        ringLeds[index].r = 255;
        ringLeds[index].g = 0;
        ringLeds[index].b = 0;
      }
    }
  }
  ringBusShow();
}

// ── Network-task shared state ─────────────────────────────────────────────
struct TsSnapshot {
  float t4c, vcc4c, d1_4c, d2_4c;
  float t4f, vcc4f, d1_4f;
  bool ok4c, ok4f, heater, accOk;
  char accName[12];
};
static TsSnapshot        g_tsSnap{};
static portMUX_TYPE      g_snapMux      = portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t g_tsPublishSem = nullptr;
static SemaphoreHandle_t g_tsPollSem    = nullptr;
static volatile int      g_lastTsCode   = 0;
static volatile uint32_t g_lastTsPushMs = 0;

void setHeater(bool on) {
  heaterOn = on;
  digitalWrite(PIN_HEATER_RELAY, on ? HIGH : LOW);
  Serial.printf("[HEATER] %s\n", on ? "ON" : "OFF");
}

void handleSerialCommands() {
  while (Serial.available()) {
    static char cmdBuf[32];
    static uint8_t cmdLen = 0;
    char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (cmdLen > 0) {
        cmdBuf[cmdLen] = '\0';
        if (strcmp(cmdBuf, "HEATER ON") == 0) {
          setHeater(true);
        } else if (strcmp(cmdBuf, "HEATER OFF") == 0) {
          setHeater(false);
        } else if (strcmp(cmdBuf, "RING OFF") == 0) {
          setRingPattern(RingPattern::Off);
        } else if (strcmp(cmdBuf, "RING RAINBOW") == 0) {
          setRingPattern(RingPattern::Rainbow);
        } else if (strcmp(cmdBuf, "RING THEATER") == 0) {
          setRingPattern(RingPattern::Theater);
        } else if (strcmp(cmdBuf, "RING WHITE") == 0) {
          setRingPattern(RingPattern::White);
        } else if (strcmp(cmdBuf, "RING RED") == 0) {
          setRingPattern(RingPattern::Red);
        } else if (strcmp(cmdBuf, "RING GREEN") == 0) {
          setRingPattern(RingPattern::Green);
        } else if (strcmp(cmdBuf, "RING BLUE") == 0) {
          setRingPattern(RingPattern::Blue);
        } else if (strcmp(cmdBuf, "RING AUTO") == 0) {
          setRingPattern(RingPattern::Auto);
        }
        cmdLen = 0;
      }
    } else if (cmdLen < 31) {
      cmdBuf[cmdLen++] = c;
    }
  }
}

void applyLedCommand(long cmd) {
  uint32_t color = statusPixel.Color(0, 0, 0);

  switch (cmd) {
    case 1:
      color = statusPixel.Color(255, 0, 0);
      break;
    case 2:
      color = statusPixel.Color(0, 255, 0);
      break;
    case 3:
      color = statusPixel.Color(0, 0, 255);
      break;
    case 4:
      color = statusPixel.Color(255, 255, 255);
      break;
    default:
      color = statusPixel.Color(0, 0, 0);
      break;
  }

  statusPixel.setPixelColor(0, color);
  statusPixel.show();
}

// pollThingSpeakControl: signals the network task to read Field 8.
void pollThingSpeakControl() {
  if (g_tsPollSem) xSemaphoreGive(g_tsPollSem);
}

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("[WIFI] begin %s\n", WIFI_SSID);
}

// publishToThingSpeak: snapshots sensor data and signals the network task.
// Returns immediately — actual HTTP write happens on core 0.
void publishToThingSpeak() {
  portENTER_CRITICAL(&g_snapMux);
  g_tsSnap.t4c   = sample4c.tempC;  g_tsSnap.vcc4c = sample4c.vcc;
  g_tsSnap.d1_4c = sample4c.d1mv;   g_tsSnap.d2_4c = sample4c.d2mv;
  g_tsSnap.t4f   = sample4f.tempC;  g_tsSnap.vcc4f = sample4f.vcc;
  g_tsSnap.d1_4f = sample4f.d1mv;
  g_tsSnap.ok4c  = sample4c.ok;     g_tsSnap.ok4f  = sample4f.ok;
  g_tsSnap.heater = heaterOn;        g_tsSnap.accOk  = accelSample.ok;
  snprintf(g_tsSnap.accName, sizeof(g_tsSnap.accName), "%s", accelName);
  portEXIT_CRITICAL(&g_snapMux);
  if (g_tsPublishSem) xSemaphoreGive(g_tsPublishSem);
}
uint16_t touchBaseline = 0;
uint16_t touchThreshold = 0;
bool touchPressed = false;
uint32_t lastTouchEventMs = 0;

const char *pageName(UiPage page) {
  switch (page) {
    case UiPage::BootScanOled:
      return "BOOT_SCAN_8_9";
    case UiPage::BootScanLtc:
      return "BOOT_SCAN_17_18";
    case UiPage::Summary:
      return "SUMMARY";
    case UiPage::Detail4C:
      return "DETAIL_4C";
    case UiPage::Detail4F:
      return "DETAIL_4F";
    case UiPage::Accel:
      return "ACCEL";
    case UiPage::Status:
      return "STATUS";
    default:
      return "UNKNOWN";
  }
}

const char *qualityName(LtcQuality quality) {
  switch (quality) {
    case LtcQuality::Good:
      return "GOOD";
    case LtcQuality::Missing:
      return "MISS";
    case LtcQuality::AllZero:
      return "ZERO";
    case LtcQuality::ShortSuspect:
      return "SHORT";
    case LtcQuality::OutOfRange:
      return "RANGE";
    case LtcQuality::ReadFail:
      return "READ";
    default:
      return "UNK";
  }
}

float sampleOrSentinel(const LtcSample &s, float value) {
  return s.ok ? value : 888.0f;
}

bool ltcWriteReg(uint8_t addr, uint8_t reg, uint8_t value) {
  ltcBus.beginTransmission(addr);
  ltcBus.write(reg);
  ltcBus.write(value);
  return ltcBus.endTransmission() == 0;
}

bool ltcRead14Detailed(uint8_t addr, uint8_t msbReg, int16_t &code, uint8_t &txStatus, uint8_t &rxCount) {
  auto tryRead = [&](bool repeatedStart) -> bool {
    ltcBus.beginTransmission(addr);
    ltcBus.write(msbReg);
    txStatus = ltcBus.endTransmission(!repeatedStart);
    if (txStatus != 0) {
      rxCount = 0;
      return false;
    }

    rxCount = static_cast<uint8_t>(ltcBus.requestFrom(static_cast<int>(addr), 2));
    if (rxCount != 2) {
      return false;
    }

    uint16_t raw = (static_cast<uint16_t>(ltcBus.read()) << 8) | ltcBus.read();
    code = static_cast<int16_t>(raw & 0x7FFF);  // strip DATA_VALID bit
    return true;
  };

  if (tryRead(true)) {
    return true;
  }

  // Fallback for devices/wiring that behave better with a stop between phases.
  return tryRead(false);
}

float ltcCodeToSingleEnded(int16_t code) {
  int16_t sign = 1;
  if (code >> 14) {
    code = (code ^ 0x7FFF) + 1;
    sign = -1;
  }
  code &= 0x3FFF;
  return static_cast<float>(code) * LTC_SINGLE_ENDED_LSB * sign;
}

float ltcCodeToVcc(int16_t code) {
  return ltcCodeToSingleEnded(code) + 2.5f;
}

float ltcCodeToTempC(int16_t code) {
  code &= 0x1FFF;
  if (code & 0x1000) {
    code |= static_cast<int16_t>(0xE000);
  }
  return static_cast<float>(code) * LTC_TEMP_LSB;
}

bool configureLtc(uint8_t addr) {
  if (!ltcWriteReg(addr, LTC_REG_CONTROL, LTC_CTRL_REPEATED_C)) {
    return false;
  }
  return ltcWriteReg(addr, LTC_REG_TRIGGER, 0x01);
}

LtcSample readLtc(uint8_t addr, LtcDiag &diag) {
  LtcSample s{};
  s.ok = false;
  s.quality = static_cast<uint8_t>(LtcQuality::ReadFail);

  int16_t tintCode = 0;
  int16_t vccCode = 0;
  int16_t v1Code = 0;
  int16_t v2Code = 0;
  int16_t v3Code = 0;
  int16_t v4Code = 0;

  uint8_t txStatus = 0;
  uint8_t rxCount = 0;

  auto readReg = [&](uint8_t reg, int16_t &value) -> bool {
    for (uint8_t attempt = 0; attempt < 3; attempt++) {
      if (ltcRead14Detailed(addr, reg, value, txStatus, rxCount)) {
        return true;
      }
      delay(1);
    }

    diag.lastFailReg = reg;
    diag.lastTxStatus = txStatus;
    diag.lastRxCount = rxCount;
    diag.lastFailStage = (txStatus != 0) ? LtcFailStage::ReadAddr : LtcFailStage::ReadData;
    return false;
  };

  if (!readReg(LTC_REG_TINT_MSB, tintCode) ||
      !readReg(LTC_REG_VCC_MSB, vccCode) ||
      !readReg(LTC_REG_V1_MSB, v1Code) ||
      !readReg(LTC_REG_V2_MSB, v2Code) ||
      !readReg(LTC_REG_V3_MSB, v3Code) ||
      !readReg(LTC_REG_V4_MSB, v4Code)) {
    diag.readFailCount++;
    s.quality = static_cast<uint8_t>(LtcQuality::ReadFail);
    return s;
  }

  if (tintCode == 0 && vccCode == 0 && v1Code == 0 && v2Code == 0 && v3Code == 0 && v4Code == 0) {
    diag.readFailCount++;
    diag.allZeroCount++;
    s.quality = static_cast<uint8_t>(LtcQuality::AllZero);
    diag.lastFailStage = LtcFailStage::ReadData;
    diag.lastFailReg = LTC_REG_TINT_MSB;
    return s;
  }

  s.tempC = ltcCodeToTempC(tintCode);
  s.vcc = ltcCodeToVcc(vccCode);
  s.v1 = ltcCodeToSingleEnded(v1Code);
  s.v2 = ltcCodeToSingleEnded(v2Code);
  s.v3 = ltcCodeToSingleEnded(v3Code);
  s.v4 = ltcCodeToSingleEnded(v4Code);
  s.d1mv = (s.v1 - s.v2) * 1000.0f;
  s.d2mv = (s.v3 - s.v4) * 1000.0f;

  if (s.tempC < -60.0f || s.tempC > 180.0f || s.vcc < 2.7f || s.vcc > 5.8f) {
    diag.readFailCount++;
    diag.rangeFailCount++;
    s.quality = static_cast<uint8_t>(LtcQuality::OutOfRange);
    diag.lastFailStage = LtcFailStage::ReadData;
    diag.lastFailReg = LTC_REG_VCC_MSB;
    return s;
  }

  if (s.vcc <= 2.62f && fabsf(s.tempC) <= 0.25f) {
    diag.readFailCount++;
    diag.shortFailCount++;
    s.quality = static_cast<uint8_t>(LtcQuality::ShortSuspect);
    diag.lastFailStage = LtcFailStage::ReadData;
    diag.lastFailReg = LTC_REG_VCC_MSB;
    return s;
  }

  s.ok = true;
  s.quality = static_cast<uint8_t>(LtcQuality::Good);
  diag.okReadCount++;
  diag.consecutiveFailCount = 0;
  diag.lastFailStage = LtcFailStage::None;
  diag.lastFailReg = 0;
  diag.lastTxStatus = 0;
  diag.lastRxCount = 2;
  return s;
}

void drawSummaryPage(const LtcSample &a, const LtcSample &b) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.print("LTC2990 Summary");

  oled.setCursor(0, 24);
  if (a.ok) {
    oled.printf("4C T:%5.1fC V:%4.2f", a.tempC, a.vcc);
  } else {
    oled.print("4C read fail");
  }

  oled.setCursor(0, 38);
  if (b.ok) {
    oled.printf("4F T:%5.1fC V:%4.2f", b.tempC, b.vcc);
  } else {
    oled.print("4F read fail");
  }

  oled.setCursor(0, 52);
  // WiFi + Heater + last TS code in compact form
  char statusLine[22];
  const char *wf = (WiFi.status() == WL_CONNECTED) ? "W:OK" : "W:--";
  snprintf(statusLine, sizeof(statusLine), "%s H:%s TS:%d",
           wf, heaterOn ? "ON" : "OF", (int)g_lastTsCode);
  oled.print(statusLine);
  oled.sendBuffer();
}

void drawChannelPage(uint8_t addr, const LtcSample &s) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.printf("LTC 0x%02X", addr);

  if (!s.ok) {
    oled.setCursor(0, 26);
    oled.print("Read fail");
    oled.sendBuffer();
    return;
  }

  oled.setCursor(0, 22);
  oled.printf("T:%5.1fC V:%4.2f", s.tempC, s.vcc);
  oled.setCursor(0, 34);
  oled.printf("V1:%6.3f  V2:%6.3f", s.v1, s.v2);
  oled.setCursor(0, 46);
  oled.printf("V3:%6.3f  V4:%6.3f", s.v3, s.v4);
  oled.setCursor(0, 58);
  oled.printf("D1:%6.1fmV D2:%6.1f", s.d1mv, s.d2mv);
  oled.sendBuffer();
}

const char *failStageName(LtcFailStage stage) {
  switch (stage) {
    case LtcFailStage::None:
      return "none";
    case LtcFailStage::Probe:
      return "probe";
    case LtcFailStage::ConfigCtrl:
      return "cfg_ctrl";
    case LtcFailStage::ConfigTrig:
      return "cfg_trig";
    case LtcFailStage::ReadAddr:
      return "read_addr";
    case LtcFailStage::ReadData:
      return "read_data";
    default:
      return "unknown";
  }
}

void updateLtcSensor(uint8_t addr, LtcDiag &diag, LtcSample &sample, bool presentFlag) {
  diag.present = presentFlag;
  if (!presentFlag) {
    sample.ok = false;
    sample.quality = static_cast<uint8_t>(LtcQuality::Missing);
    diag.configured = false;
    diag.consecutiveFailCount++;
    diag.probeFailCount++;
    diag.lastFailStage = LtcFailStage::Probe;
    return;
  }

  if (!diag.configured) {
    if (!ltcWriteReg(addr, LTC_REG_CONTROL, LTC_CTRL_REPEATED_C)) {
      diag.configFailCount++;
      diag.consecutiveFailCount++;
      diag.lastFailStage = LtcFailStage::ConfigCtrl;
      sample.ok = false;
      sample.quality = static_cast<uint8_t>(LtcQuality::ReadFail);
      return;
    }
    if (!ltcWriteReg(addr, LTC_REG_TRIGGER, 0x01)) {
      diag.configFailCount++;
      diag.consecutiveFailCount++;
      diag.lastFailStage = LtcFailStage::ConfigTrig;
      sample.ok = false;
      sample.quality = static_cast<uint8_t>(LtcQuality::ReadFail);
      return;
    }
    diag.configured = true;
  }

  sample = readLtc(addr, diag);
  if (!sample.ok) {
    diag.consecutiveFailCount++;
    // If read path hiccups but device is present, re-apply config and retry once.
    if (ltcWriteReg(addr, LTC_REG_CONTROL, LTC_CTRL_REPEATED_C) && ltcWriteReg(addr, LTC_REG_TRIGGER, 0x01)) {
      diag.recoverCount++;
      sample = readLtc(addr, diag);
      if (!sample.ok && diag.consecutiveFailCount >= 3) {
        // Escalate recovery: force a clean bus re-init after repeated faults.
        ltcBus.begin(PIN_LTC_SDA, PIN_LTC_SCL, LTC_I2C_CLOCK_HZ);
        ltcBus.setTimeOut(I2C_TIMEOUT_MS);
        diag.configured = false;
      }
    } else {
      diag.configured = false;
    }
  }
}

bool probeAddr(TwoWire &bus, uint8_t addr) {
  bus.beginTransmission(addr);
  return bus.endTransmission() == 0;
}

void scanBus(TwoWire &bus, BusScanInfo &info) {
  info.count = 0;
  info.has4c = false;
  info.has4f = false;
  info.list[0] = '\0';

  size_t pos = 0;
  const size_t maxLen = sizeof(info.list) - 1;

  for (uint8_t addr = 0x03; addr < 0x78; addr++) {
    bus.beginTransmission(addr);
    if (bus.endTransmission() == 0) {
      info.count++;
      if (addr == LTC_ADDR_GND_GND) {
        info.has4c = true;
      }
      if (addr == LTC_ADDR_SECONDARY) {
        info.has4f = true;
      }

      if (pos + 5 < maxLen) {
        int n = snprintf(&info.list[pos], maxLen - pos + 1, "0x%02X ", addr);
        if (n > 0) {
          pos += static_cast<size_t>(n);
        }
      }
    }
  }

  if (info.count == 0) {
    snprintf(info.list, sizeof(info.list), "none");
  }
}

uint8_t pickOledAddress(const BusScanInfo &scan) {
  // Typical OLED addresses are 0x3C/0x3D; prefer those if present.
  if (probeAddr(Wire, 0x3C)) {
    return 0x3C;
  }
  if (probeAddr(Wire, 0x3D)) {
    return 0x3D;
  }

  for (uint8_t addr = 0x03; addr < 0x78; addr++) {
    if (probeAddr(Wire, addr)) {
      return addr;
    }
  }

  (void)scan;
  return 0;
}

void drawScanPage(const BusScanInfo &oledScan, const BusScanInfo &ltcScan) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.print("I2C Scan Debug");

  oled.setCursor(0, 24);
  oled.printf("OLED bus C:%u", oledScan.count);
  oled.setCursor(0, 34);
  oled.print(oledScan.list);

  oled.setCursor(0, 48);
  oled.printf("LTC bus C:%u", ltcScan.count);
  oled.setCursor(0, 58);
  oled.print(ltcScan.list);
  oled.sendBuffer();
}

void drawSingleBusScanPage(const char *name, uint8_t sda, uint8_t scl, const BusScanInfo &scan) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.printf("I2C Scan %s", name);
  oled.setCursor(0, 24);
  oled.printf("SDA:%u SCL:%u", sda, scl);
  oled.setCursor(0, 38);
  oled.printf("Count:%u", scan.count);
  oled.setCursor(0, 52);
  oled.print(scan.list);
  oled.sendBuffer();
}

void drawAccelPage(const AccelSample &a) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.printf("Accel %s", accelName);

  if (!a.ok) {
    oled.setCursor(0, 26);
    oled.print("No accel data");
    oled.sendBuffer();
    return;
  }

  oled.setCursor(0, 24);
  oled.printf("X:%7.2f", a.x);
  oled.setCursor(0, 38);
  oled.printf("Y:%7.2f", a.y);
  oled.setCursor(0, 52);
  oled.printf("Z:%7.2f", a.z);
  oled.sendBuffer();
}

void drawStatusPage() {
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 10);
  oled.print("WiFi / TS Status");

  // WiFi status
  oled.setCursor(0, 22);
  if (WiFi.status() == WL_CONNECTED) {
    oled.printf("W:OK  RSSI:%d", (int)WiFi.RSSI());
  } else {
    oled.print("W:CONNECTING...");
  }

  // ThingSpeak: last code + seconds since last ok push
  oled.setCursor(0, 34);
  if (g_lastTsPushMs) {
    uint32_t sec = (millis() - g_lastTsPushMs) / 1000;
    oled.printf("TS:%d  %lus ago", (int)g_lastTsCode, (unsigned long)sec);
  } else {
    oled.printf("TS:%d  no push yet", (int)g_lastTsCode);
  }

  // Heater
  oled.setCursor(0, 46);
  oled.printf("Heater: %s", heaterOn ? "ON" : "OFF");

  // Temp summary
  oled.setCursor(0, 58);
  if (sample4c.ok && sample4f.ok) {
    oled.printf("4C:%.1fC 4F:%.1fC", sample4c.tempC, sample4f.tempC);
  } else if (sample4c.ok) {
    oled.printf("4C:%.1fC 4F:MISS", sample4c.tempC);
  } else if (sample4f.ok) {
    oled.printf("4C:MISS 4F:%.1fC", sample4f.tempC);
  } else {
    oled.print("4C:MISS 4F:MISS");
  }
  oled.sendBuffer();
}

void setAccelName(const char *name) {
  snprintf(accelName, sizeof(accelName), "%s", name);
}

void detectAccelerometer() {
  if (lis3dh.begin(0x18) || lis3dh.begin(0x19)) {
    lis3dh.setRange(LIS3DH_RANGE_4_G);
    accelType = AccelType::LIS3DH;
    setAccelName("LIS3DH");
    Serial.println("Accelerometer: LIS3DH FOUND");
    return;
  }

  if (mpu6050.begin(0x68, &ltcBus) || mpu6050.begin(0x69, &ltcBus)) {
    mpu6050.setAccelerometerRange(MPU6050_RANGE_4_G);
    accelType = AccelType::MPU6050;
    setAccelName("MPU6050");
    Serial.println("Accelerometer: MPU6050 FOUND");
    return;
  }

  accelType = AccelType::None;
  setAccelName("NONE");
  Serial.println("Accelerometer: NONE");
}

void updateAccelSample() {
  accelSample.ok = false;

  if (accelType == AccelType::LIS3DH) {
    sensors_event_t event;
    lis3dh.getEvent(&event);
    accelSample.x = event.acceleration.x;
    accelSample.y = event.acceleration.y;
    accelSample.z = event.acceleration.z;
    if (isfinite(accelSample.x) && isfinite(accelSample.y) && isfinite(accelSample.z) &&
        (fabsf(accelSample.x) + fabsf(accelSample.y) + fabsf(accelSample.z) >= 0.5f)) {
      accelSample.ok = true;
    }
    return;
  }

  if (accelType == AccelType::MPU6050) {
    sensors_event_t a;
    sensors_event_t g;
    sensors_event_t t;
    mpu6050.getEvent(&a, &g, &t);
    accelSample.x = a.acceleration.x;
    accelSample.y = a.acceleration.y;
    accelSample.z = a.acceleration.z;
    if (isfinite(accelSample.x) && isfinite(accelSample.y) && isfinite(accelSample.z) &&
        (fabsf(accelSample.x) + fabsf(accelSample.y) + fabsf(accelSample.z) >= 0.5f)) {
      accelSample.ok = true;
    }
  }
}

void drawCurrentPage(bool pageChanged) {
  if (pageChanged) {
    lastPageChangeMs = millis();
    Serial.printf("[PAGE] %s at %lu ms\n", pageName(currentPage), static_cast<unsigned long>(lastPageChangeMs));
  }

  switch (currentPage) {
    case UiPage::BootScanOled:
      drawSingleBusScanPage("8/9", PIN_OLED_SDA, PIN_OLED_SCL, oledScan);
      break;
    case UiPage::BootScanLtc:
      drawSingleBusScanPage("17/18", PIN_LTC_SDA, PIN_LTC_SCL, ltcScan);
      break;
    case UiPage::Summary:
      drawSummaryPage(sample4c, sample4f);
      break;
    case UiPage::Detail4C:
      drawChannelPage(LTC_ADDR_GND_GND, sample4c);
      break;
    case UiPage::Detail4F:
      drawChannelPage(LTC_ADDR_SECONDARY, sample4f);
      break;
    case UiPage::Accel:
      drawAccelPage(accelSample);
      break;
    case UiPage::Status:
      drawStatusPage();
      break;
  }
}

bool onSensorRefresh(void *) {
  uint32_t now = millis();

  // WiFi managed by network task — no blocking call here.

  updateLtcSensor(LTC_ADDR_GND_GND, diag4c, sample4c, ltc4cPresent);
  updateLtcSensor(LTC_ADDR_SECONDARY, diag4f, sample4f, ltc4fPresent);

  if ((now - lastAccelReadMs) >= ACCEL_REFRESH_MS) {
    updateAccelSample();
    lastAccelReadMs = now;
  }

  // Keep currently shown values alive at 2Hz while staying on a page.
  if (bootSequenceDone) {
    drawCurrentPage(false);
  }

  if (now - lastSensorLogMs >= 1000) {
    Serial.printf("[SENSOR] t=%lu 4C=%s(%s) 4F=%s(%s) ACC=%s HEATER=%s\n",
                  static_cast<unsigned long>(now),
                  sample4c.ok ? "OK" : "MISS",
                  qualityName(static_cast<LtcQuality>(sample4c.quality)),
                  sample4f.ok ? "OK" : "MISS",
                  qualityName(static_cast<LtcQuality>(sample4f.quality)),
                  accelSample.ok ? accelName : "NONE",
                  heaterOn ? "ON" : "OFF");

    Serial.printf("[4FDBG] present=%u cfg=%u ok=%lu rf=%lu cf=%lu pf=%lu zf=%lu sf=%lu rnf=%lu rec=%lu cfail=%lu stage=%s reg=0x%02X tx=%u rx=%u\n",
                  diag4f.present ? 1 : 0,
                  diag4f.configured ? 1 : 0,
                  static_cast<unsigned long>(diag4f.okReadCount),
                  static_cast<unsigned long>(diag4f.readFailCount),
                  static_cast<unsigned long>(diag4f.configFailCount),
                  static_cast<unsigned long>(diag4f.probeFailCount),
                  static_cast<unsigned long>(diag4f.allZeroCount),
                  static_cast<unsigned long>(diag4f.shortFailCount),
                  static_cast<unsigned long>(diag4f.rangeFailCount),
                  static_cast<unsigned long>(diag4f.recoverCount),
                  static_cast<unsigned long>(diag4f.consecutiveFailCount),
                  failStageName(diag4f.lastFailStage),
                  diag4f.lastFailReg,
                  diag4f.lastTxStatus,
                  diag4f.lastRxCount);

    Serial.printf("[4CDBG] present=%u cfg=%u ok=%lu rf=%lu cf=%lu pf=%lu zf=%lu sf=%lu rnf=%lu rec=%lu cfail=%lu stage=%s reg=0x%02X tx=%u rx=%u\n",
            diag4c.present ? 1 : 0,
            diag4c.configured ? 1 : 0,
            static_cast<unsigned long>(diag4c.okReadCount),
            static_cast<unsigned long>(diag4c.readFailCount),
            static_cast<unsigned long>(diag4c.configFailCount),
            static_cast<unsigned long>(diag4c.probeFailCount),
            static_cast<unsigned long>(diag4c.allZeroCount),
            static_cast<unsigned long>(diag4c.shortFailCount),
            static_cast<unsigned long>(diag4c.rangeFailCount),
            static_cast<unsigned long>(diag4c.recoverCount),
            static_cast<unsigned long>(diag4c.consecutiveFailCount),
            failStageName(diag4c.lastFailStage),
            diag4c.lastFailReg,
            diag4c.lastTxStatus,
            diag4c.lastRxCount);

    Serial.printf("[4C_DIODE] Q=%s D1=%0.2fmV D2=%0.2fmV TINT=%0.2fC VCC=%0.3fV\n",
                  qualityName(static_cast<LtcQuality>(sample4c.quality)),
                  sampleOrSentinel(sample4c, sample4c.d1mv),
                  sampleOrSentinel(sample4c, sample4c.d2mv),
                  sampleOrSentinel(sample4c, sample4c.tempC),
                  sampleOrSentinel(sample4c, sample4c.vcc));

    Serial.printf("[4F_DIODE] Q=%s D1=%0.2fmV D2=%0.2fmV TINT=%0.2fC VCC=%0.3fV\n",
                  qualityName(static_cast<LtcQuality>(sample4f.quality)),
                  sampleOrSentinel(sample4f, sample4f.d1mv),
                  sampleOrSentinel(sample4f, sample4f.d2mv),
                  sampleOrSentinel(sample4f, sample4f.tempC),
                  sampleOrSentinel(sample4f, sample4f.vcc));

    lastSensorLogMs = now;
  }

  if (now - lastAddrDumpMs >= 5000) {
    BusScanInfo liveScan{};
    scanBus(ltcBus, liveScan);
    ltc4cPresent = liveScan.has4c;
    ltc4fPresent = liveScan.has4f;
    Serial.printf("[LIVE SCAN 17/18] count=%u addrs=%s\n", liveScan.count, liveScan.list);
    lastAddrDumpMs = now;
  }

  if ((now - lastThingSpeakPushMs) >= THINGSPEAK_PUBLISH_MS) {
    publishToThingSpeak();
    lastThingSpeakPushMs = now;
  }

  if ((now - lastThingSpeakControlPollMs) >= THINGSPEAK_CONTROL_POLL_MS) {
    pollThingSpeakControl();
    lastThingSpeakControlPollMs = now;
  }

  return true;
}

// ─── Network task (runs on core 0) ───────────────────────────────────────────
// Handles: WiFi watchdog (reconnect every 60 s if lost), ThingSpeak publish,
// ThingSpeak LED-field poll.  Never blocks the sensor/OLED loop on core 1.
static void networkTask(void *) {
  uint32_t noConnSince  = 0;   // millis() when disconnect first detected
  uint32_t lastReconnMs = 0;   // millis() of last WiFi.begin() attempt

  for (;;) {
    uint32_t now = (uint32_t)millis();
    wl_status_t wst = WiFi.status();

    // ── WiFi watchdog ────────────────────────────────────────────────────────
    if (wst != WL_CONNECTED) {
      if (noConnSince == 0) noConnSince = now ? now : 1;
      uint32_t gap = now - noConnSince;

      if (now - lastReconnMs >= 10000) {   // retry every 10 s
        lastReconnMs = now;
        if (gap >= 60000) {                // force full reset after 60 s
          Serial.printf("[WIFI] force reset after %lus disconnected\n",
                        (unsigned long)(gap / 1000));
          WiFi.disconnect(true);
          vTaskDelay(pdMS_TO_TICKS(400));
        }
        WiFi.mode(WIFI_STA);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        Serial.printf("[WIFI] reconnect attempt gap=%lus\n",
                      (unsigned long)(gap / 1000));
      }
    } else {
      if (noConnSince) {
        noConnSince = 0;
        Serial.printf("[WIFI] connected RSSI=%d IP=%s\n",
                      (int)WiFi.RSSI(), WiFi.localIP().toString().c_str());
      }
    }

    // ── ThingSpeak publish ───────────────────────────────────────────────────
    if (g_tsPublishSem && xSemaphoreTake(g_tsPublishSem, 0) == pdTRUE) {
      if (WiFi.status() == WL_CONNECTED) {
        // Copy snapshot (written under critical section by core 1)
        TsSnapshot snap;
        portENTER_CRITICAL(&g_snapMux);
        snap = g_tsSnap;
        portEXIT_CRITICAL(&g_snapMux);

        auto tsVal = [](bool ok, float v) -> float { return ok ? v : 888.0f; };
        ThingSpeak.setField(1, tsVal(snap.ok4c, snap.t4c));
        ThingSpeak.setField(2, tsVal(snap.ok4c, snap.vcc4c));
        ThingSpeak.setField(3, tsVal(snap.ok4c, snap.d1_4c));
        ThingSpeak.setField(4, tsVal(snap.ok4c, snap.d2_4c));
        ThingSpeak.setField(5, tsVal(snap.ok4f, snap.t4f));
        ThingSpeak.setField(6, tsVal(snap.ok4f, snap.vcc4f));
        ThingSpeak.setField(7, tsVal(snap.ok4f, snap.d1_4f));

        String st = String("4C:") + (snap.ok4c ? "OK" : "MISS")
                  + " 4F:" + (snap.ok4f ? "OK" : "MISS")
                  + " H=" + (snap.heater ? "ON" : "OFF")
                  + " A=" + snap.accName;
        ThingSpeak.setStatus(st);

        int code = ThingSpeak.writeFields(THINGSPEAK_CHANNEL_ID,
                                          THINGSPEAK_WRITE_API_KEY);
        g_lastTsCode = code;
        if (code == 200) {
          g_lastTsPushMs = (uint32_t)millis();
          Serial.printf("[TS] push OK code=200 RSSI=%d\n", (int)WiFi.RSSI());
        } else {
          Serial.printf("[TS] push failed http=%d\n", code);
          // If we get auth/server errors repeatedly, force WiFi reconnect
          if (code == -301 || code == -302 || code <= -300) {
            noConnSince = now ? now : 1;  // trigger watchdog cycle
          }
        }
      } else {
        Serial.println("[TS] skip push: no WiFi");
      }
    }

    // ── ThingSpeak LED-field poll ────────────────────────────────────────────
    if (g_tsPollSem && xSemaphoreTake(g_tsPollSem, 0) == pdTRUE) {
      if (WiFi.status() == WL_CONNECTED) {
        long cmd = ThingSpeak.readLongField(THINGSPEAK_CHANNEL_ID,
                                            THINGSPEAK_LED_FIELD,
                                            THINGSPEAK_READ_API_KEY);
        int httpSt = ThingSpeak.getLastReadStatus();
        if (httpSt == 200) {
          if (cmd != ledCommand) {
            ledCommand = cmd;
            applyLedCommand(ledCommand);
            Serial.printf("[TS_CTRL] f%u=%ld applied\n",
                          THINGSPEAK_LED_FIELD, ledCommand);
          }
        } else {
          Serial.printf("[TS_CTRL] read failed http=%d\n", httpSt);
        }
      }
    }

    vTaskDelay(pdMS_TO_TICKS(250));
  }
}

bool onPageAdvance(void *) {
  Serial.printf("[TIMER] runtime page advance from %s\n", pageName(currentPage));

  if (currentPage == UiPage::Summary) {
    currentPage = UiPage::Detail4C;
  } else if (currentPage == UiPage::Detail4C) {
    currentPage = UiPage::Detail4F;
  } else if (currentPage == UiPage::Detail4F) {
    currentPage = UiPage::Status;
  } else if (currentPage == UiPage::Status) {
    currentPage = UiPage::Accel;
  } else {
    currentPage = UiPage::Summary;
  }

  drawCurrentPage(true);
  return true;
}

bool onBootToLtcPage(void *) {
  currentPage = UiPage::BootScanLtc;
  Serial.println("[BOOT] Switch to 17/18 scan page");
  drawCurrentPage(true);
  return false;
}

bool onBootToRuntime(void *) {
  bootSequenceDone = true;
  currentPage = UiPage::Summary;
  Serial.println("[BOOT] Enter runtime page rotation");
  drawCurrentPage(true);
  appTimer.every(RUN_PAGE_MS, onPageAdvance);
  return false;
}

void initTouch() {
  uint32_t acc = 0;
  const uint8_t samples = 16;
  for (uint8_t i = 0; i < samples; i++) {
    acc += touchRead(PIN_TOUCH_NEXT);
    delay(5);
  }
  touchBaseline = static_cast<uint16_t>(acc / samples);
  touchThreshold = static_cast<uint16_t>(touchBaseline * 70UL / 100UL);
  Serial.printf("[TOUCH] pin=%u baseline=%u threshold=%u\n", PIN_TOUCH_NEXT, touchBaseline, touchThreshold);
}

void handleTouchNextPage() {
  if (!bootSequenceDone) {
    return;
  }

  uint16_t raw = touchRead(PIN_TOUCH_NEXT);
  bool nowPressed = (raw < touchThreshold);
  uint32_t now = millis();

  if (nowPressed && !touchPressed && (now - lastTouchEventMs) > TOUCH_DEBOUNCE_MS) {
    lastTouchEventMs = now;
    Serial.printf("[TOUCH] next-page raw=%u\n", raw);
    onPageAdvance(nullptr);
  }

  touchPressed = nowPressed;
}

void handleClockButton() {
  bool nowPressed = digitalRead(PIN_CLOCK_BUTTON) == LOW;
  uint32_t now = millis();

  if (nowPressed && !clockButtonPressed && (now - lastClockButtonEventMs) > TOUCH_DEBOUNCE_MS) {
    lastClockButtonEventMs = now;
    apa102ClockMode = static_cast<uint8_t>((apa102ClockMode + 1) % APA102_CLOCK_MODE_COUNT);
    Serial.printf("[LED CLOCK] mode=%u half-period=%u us\n",
                  apa102ClockMode, APA102_CLOCK_HALF_PERIOD_US[apa102ClockMode]);
  }

  clockButtonPressed = nowPressed;
}

void setup() {
  Serial.begin(115200);
  delay(300);

  // Enable internal pullups on both I2C buses before initialization.
  // External pullups are still preferred, but this helps with noisy/disconnected lines.
  pinMode(PIN_OLED_SDA, INPUT_PULLUP);
  pinMode(PIN_OLED_SCL, INPUT_PULLUP);
  pinMode(PIN_LTC_SDA, INPUT_PULLUP);
  pinMode(PIN_LTC_SCL, INPUT_PULLUP);

  // Keep OLED on requested bus pins.
  Wire.begin(PIN_OLED_SDA, PIN_OLED_SCL);
  Wire.setClock(OLED_I2C_CLOCK_HZ);
  Wire.setTimeOut(I2C_TIMEOUT_MS);

  // Put LTC2990 devices on a separate bus.
  ltcBus.begin(PIN_LTC_SDA, PIN_LTC_SCL, LTC_I2C_CLOCK_HZ);
  ltcBus.setTimeOut(I2C_TIMEOUT_MS);

  Serial.println();
  Serial.println("=== ESP32-S3 OLED + dual LTC2990 ===");
  Serial.printf("OLED bus: SDA=%u SCL=%u\n", PIN_OLED_SDA, PIN_OLED_SCL);
  Serial.printf("LTC  bus: SDA=%u SCL=%u\n", PIN_LTC_SDA, PIN_LTC_SCL);
  Serial.printf("LTC  bus clock: %lu Hz\n", static_cast<unsigned long>(LTC_I2C_CLOCK_HZ));
  Serial.printf("RING bus: DATA=%u CLK=%u COUNT=%u\n", PIN_RING_DATA, PIN_RING_CLOCK, LED_RING_COUNT);
  Serial.printf("ARRAY bus: DATA=%u CLK=%u COUNT=%u\n", PIN_ARRAY_DATA, PIN_ARRAY_CLOCK, LED_RING_COUNT);
  Serial.printf("Touch pin: GPIO%u\n", PIN_TOUCH_NEXT);
  Serial.printf("Clock button: GPIO%u to GND, modes=%u\n", PIN_CLOCK_BUTTON, APA102_CLOCK_MODE_COUNT);

  pinMode(PIN_HEATER_RELAY, OUTPUT);
  digitalWrite(PIN_HEATER_RELAY, LOW);

  ThingSpeak.begin(thingSpeakClient);
  thingSpeakClient.setTimeout(8000);  // 8 s TCP read timeout (non-blocking guard)

  // Create network task on core 0; sensor/OLED loop stays on core 1.
  g_tsPublishSem = xSemaphoreCreateBinary();
  g_tsPollSem    = xSemaphoreCreateBinary();
  xTaskCreatePinnedToCore(networkTask, "net", 8192, nullptr, 1, nullptr, 0);

  statusPixel.begin();
  statusPixel.setBrightness(NEOPIXEL_BRIGHTNESS);
  applyLedCommand(0);

  pinMode(PIN_RING_DATA, OUTPUT);
  pinMode(PIN_RING_CLOCK, OUTPUT);
  pinMode(PIN_ARRAY_DATA, OUTPUT);
  pinMode(PIN_ARRAY_CLOCK, OUTPUT);
  pinMode(PIN_CLOCK_BUTTON, INPUT_PULLUP);
  digitalWrite(PIN_RING_DATA, LOW);
  digitalWrite(PIN_RING_CLOCK, LOW);
  digitalWrite(PIN_ARRAY_DATA, LOW);
  digitalWrite(PIN_ARRAY_CLOCK, LOW);
  ringSetAll(0, 0, 0);
  ringBusShow();
  ringLastModeMs = millis();
  setRingPattern(RingPattern::Auto);

  connectToWiFi();

  initTouch();

  scanBus(Wire, oledScan);
  oledDetectedAddr = pickOledAddress(oledScan);
  if (oledDetectedAddr != 0) {
    oled.setI2CAddress(static_cast<uint8_t>(oledDetectedAddr << 1));
  }

  oled.begin();
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tf);
  oled.setCursor(0, 12);
  oled.print("Init done");
  oled.setCursor(0, 26);
  if (oledDetectedAddr != 0) {
    oled.printf("OLED addr: 0x%02X", oledDetectedAddr);
  } else {
    oled.print("OLED addr: not found");
  }
  oled.sendBuffer();

  scanBus(ltcBus, ltcScan);
  ltc4cPresent = ltcScan.has4c;
  ltc4fPresent = ltcScan.has4f;
  Serial.printf("[BOOT SCAN 8/9] count=%u addrs=%s\n", oledScan.count, oledScan.list);
  if (oledDetectedAddr != 0) {
    Serial.printf("[OLED] selected address: 0x%02X\n", oledDetectedAddr);
  } else {
    Serial.println("[OLED] no I2C device found on 8/9");
  }
  Serial.printf("[BOOT SCAN 17/18] count=%u addrs=%s\n", ltcScan.count, ltcScan.list);

  bool found4c = probeAddr(ltcBus, LTC_ADDR_GND_GND);
  bool found4f = probeAddr(ltcBus, LTC_ADDR_SECONDARY);
  Serial.printf("LTC 0x4C: %s\n", found4c ? "FOUND" : "MISSING");
  Serial.printf("LTC 0x%02X: %s\n", LTC_ADDR_SECONDARY, found4f ? "FOUND" : "MISSING");
  diag4c.present = found4c;
  diag4f.present = found4f;

  detectAccelerometer();
  onSensorRefresh(nullptr);
  drawCurrentPage(true);

  appTimer.every(SENSOR_REFRESH_MS, onSensorRefresh);
  appTimer.in(BOOT_PAGE_MS, onBootToLtcPage);
  appTimer.in(BOOT_PAGE_MS * 2, onBootToRuntime);

}

void loop() {
  handleSerialCommands();
  appTimer.tick();
  handleTouchNextPage();
  handleClockButton();
  updateLedRingPattern();
}
