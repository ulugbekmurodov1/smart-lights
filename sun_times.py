"""Quyosh chiqish/botish vaqti va quyosh balandligini hisoblash (NOAA formulasi, kutubxonasiz)."""
import datetime as dt
import numpy as np

# ---- Sozlamalar (o'zingizning joyingizga moslang) ----
CITY = "Toshkent"
LAT, LON = 41.31, 69.24     # LON: sharqiy musbat
TZ = 5.0                    # UTC+5


def _eqtime_decl(gamma):
    """Vaqt tenglamasi (daqiqa) va quyosh og'ish burchagi (radian)."""
    eqtime = 229.18 * (0.000075 + 0.001868 * np.cos(gamma) - 0.032077 * np.sin(gamma)
                       - 0.014615 * np.cos(2 * gamma) - 0.040849 * np.sin(2 * gamma))
    decl = (0.006918 - 0.399912 * np.cos(gamma) + 0.070257 * np.sin(gamma)
            - 0.006758 * np.cos(2 * gamma) + 0.000907 * np.sin(2 * gamma)
            - 0.002697 * np.cos(3 * gamma) + 0.00148 * np.sin(3 * gamma))
    return eqtime, decl


def sun_times(date, lat=LAT, lon=LON, tz=TZ):
    """Berilgan sana uchun (quyosh chiqishi, quyosh botishi) -> mahalliy datetime."""
    n = date.timetuple().tm_yday
    gamma = 2 * np.pi / 365 * (n - 1)
    eqtime, decl = _eqtime_decl(gamma)
    la = np.radians(lat)
    cos_ha = np.cos(np.radians(90.833)) / (np.cos(la) * np.cos(decl)) - np.tan(la) * np.tan(decl)
    if abs(cos_ha) > 1:
        return None, None            # qutb kuni yoki tuni
    ha = np.degrees(np.arccos(cos_ha))
    rise_utc = 720 - 4 * (lon + ha) - eqtime
    set_utc = 720 - 4 * (lon - ha) - eqtime
    base = dt.datetime.combine(date, dt.time(0))
    return (base + dt.timedelta(minutes=float(rise_utc + tz * 60)),
            base + dt.timedelta(minutes=float(set_utc + tz * 60)))


def elevation_series(date, seconds, lat=LAT, lon=LON, tz=TZ):
    """Kun davomidagi har soniya uchun quyoshning ufqdan balandligi (gradus).
    seconds: 0..86399 oralig'idagi massiv (mahalliy vaqt)."""
    n = date.timetuple().tm_yday
    hour = seconds / 3600.0
    gamma = 2 * np.pi / 365 * (n - 1 + (hour - 12) / 24)
    eqtime, decl = _eqtime_decl(gamma)
    tst = hour * 60 + eqtime + 4 * lon - 60 * tz      # haqiqiy quyosh vaqti (daqiqa)
    ha = np.radians(tst / 4 - 180)
    la = np.radians(lat)
    cos_zen = np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha)
    return 90 - np.degrees(np.arccos(np.clip(cos_zen, -1, 1)))


if __name__ == "__main__":
    today = dt.date.today()
    rise, sset = sun_times(today)
    print(f"{CITY}, {today}: chiqish {rise:%H:%M}, botish {sset:%H:%M}")
