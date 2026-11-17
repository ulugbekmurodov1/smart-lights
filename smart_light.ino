/*
  Smart Light: qorong'i tushsa yonadi, tong otsa o'chadi.
  Arduino Uno/Nano va ESP32 bilan ishlaydi.

  Ulanish:
    LDR (fotorezistor):  [3.3V/5V] -- LDR --+-- [10 kOm] -- GND
                                            |
                                        LDR_PIN (o'rta nuqta)
    Rele/MOSFET moduli:  IN -> LIGHT_PIN, VCC, GND

  Yorug' bo'lsa LDR_PIN dagi kuchlanish ortadi (ko'rsatish katta).
*/

#if defined(ESP32)
  const int LDR_PIN = 34;      // faqat kirish pini (ADC1)
  const int LIGHT_PIN = 26;
  const int ADC_MAX = 4095;
#else
  const int LDR_PIN = A0;
  const int LIGHT_PIN = 7;
  const int ADC_MAX = 1023;
#endif

// ---------------- Sozlamalar ----------------
const bool RELAY_ACTIVE_HIGH = true;        // rele moduli LOW bilan yonsa: false
const float ON_BELOW_PCT = 25.0;            // shundan qorong'i -> yoqish
const float OFF_ABOVE_PCT = 40.0;           // shundan yorug' -> o'chirish
const unsigned long CONFIRM_MS = 60000UL;   // holat shuncha vaqt turg'un bo'lsa almashadi
const unsigned long SAMPLE_MS = 1000UL;     // o'lchash oralig'i
const float ALPHA = 0.2;                    // silliqlash (0..1, kichik = silliqroq)
const bool DEBUG_CSV = true;                // Serial'ga ms,sensor,silliq,holat chiqarish

bool lightOn = false;
bool pending = false;
float level = 0;
unsigned long lastSample = 0;
unsigned long pendingSince = 0;

void setLight(bool on) {
  lightOn = on;
  digitalWrite(LIGHT_PIN, (on == RELAY_ACTIVE_HIGH) ? HIGH : LOW);
}

float readPct() {                           // 10 ta o'lchov o'rtachasi, foizda
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(LDR_PIN);
    delay(2);
  }
  return 100.0 * (sum / 10.0) / ADC_MAX;
}

void setup() {
  Serial.begin(115200);
  pinMode(LIGHT_PIN, OUTPUT);
  setLight(false);
  level = readPct();
  if (DEBUG_CSV) Serial.println("ms,sensor_pct,smoothed_pct,light_on");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSample < SAMPLE_MS) return;
  lastSample = now;

  float raw = readPct();
  level += ALPHA * (raw - level);           // silliqlash: bir lahzalik xalaqitni yo'qotadi

  bool want = lightOn;
  if (!lightOn && level < ON_BELOW_PCT) want = true;        // qorong'i
  else if (lightOn && level > OFF_ABOVE_PCT) want = false;  // yorug'

  if (want != lightOn) {
    if (!pending) { pending = true; pendingSince = now; }
    else if (now - pendingSince >= CONFIRM_MS) {            // yetarlicha uzoq turdi
      setLight(want);
      pending = false;
    }
  } else {
    pending = false;
  }

  if (DEBUG_CSV) {
    Serial.print(now); Serial.print(',');
    Serial.print(raw, 1); Serial.print(',');
    Serial.print(level, 1); Serial.print(',');
    Serial.println(lightOn ? 1 : 0);
  }
}
