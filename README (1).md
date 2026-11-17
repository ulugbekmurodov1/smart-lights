# Smart Light

Qorong'i tushganda (quyosh botganda) o'zi yonadigan, tongda quyosh chiqqanda o'zi o'chadigan chiroq.
B&S loyihalaridan biri.

## Qanday ishlaydi
- **LDR (fotorezistor)** atrofdagi yorug'likni o'lchaydi.
- **Silliqlash**: bir lahzalik yorug'lik (mashina faralari, chaqmoq) hisobga olinmaydi.
- **Gisterezis**: yoqish chegarasi (25%) va o'chirish chegarasi (40%) turlicha, shuning uchun chiroq "pirpiramaydi".
- **Tasdiqlash vaqti**: holat 60 soniya turg'un bo'lgandagina chiroq almashadi (bulut o'tsa yonib-o'chmaydi).

## Papkalar
- `firmware/smart_light/` : Arduino/ESP32 kodi (haqiqiy qurilma uchun)
- `python/` : algoritmni kompyuterda sinash (simulyatsiya) va quyosh vaqtlari hisobi

## Kerakli qismlar
| Qism | Izoh |
|---|---|
| Arduino Uno/Nano yoki ESP32 | boshqaruvchi |
| LDR (fotorezistor) + 10 kOm rezistor | yorug'lik sensori |
| Rele moduli yoki MOSFET (masalan IRLZ44N) | chiroqni yoqib-o'chirish |
| LED chiroq / LED lenta (5-12 V) | yorug'lik manbai |

## Ulanish
```
3.3V/5V --- LDR ---+--- 10 kOm --- GND
                   |
                A0 (ESP32: GPIO34)

Rele IN -> pin 7 (ESP32: GPIO26), VCC -> 5V, GND -> GND
```
Xavfsizlik: 220 V tarmoq bilan ishlamang, past kuchlanishli (5-12 V) LED ishlating.

## Simulyatsiya (kompyuter yoki Google Colab)
```
cd python
pip install -r requirements.txt
python simulate.py --date 2026-11-17
python sun_times.py
```
`results/simulation.png` grafigi chiqadi: sensor ko'rsatishi, chegaralar, quyosh chiqish/botish vaqti
va "oddiy" hamda "smart" boshqaruvchining almashishlar soni.

## Haqiqiy qurilmada
1. Arduino IDE'da `firmware/smart_light/smart_light.ino` ni oching.
2. Pinlarni va `RELAY_ACTIVE_HIGH` ni o'zingizning ulanishingizga moslang.
3. Yuklang. Serial Monitor (115200) da `ms,sensor_pct,smoothed_pct,light_on` ko'rinadi.
4. Chegaralarni (`ON_BELOW_PCT`, `OFF_ABOVE_PCT`) o'z joyingizdagi yorug'likka qarab sozlang.

## Natijalar
(Simulyatsiya natijasi va qurilmaning real sinov natijalarini shu yerga yozing.)

## Kelajakdagi ishlar
- Quyosh panelidan quvvatlash (solar powerbank bilan)
- ESP32 orqali telefon ilovasida holatni ko'rish
- Harakat sensori (PIR) qo'shib, kerak bo'lganda yorqinligini oshirish
