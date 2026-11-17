"""Smart Light algoritmini bir kunlik sun'iy yorug'lik ma'lumotida sinash.

Yorug'lik quyosh balandligidan hisoblanadi, ustiga bulut, sensor shovqini va
tunda mashina faralari (xalaqit) qo'shiladi. Natija: "oddiy" va "smart"
boshqaruvchining yoqish/o'chirish vaqtlari va almashishlar soni.
Algoritm firmware/smart_light/smart_light.ino bilan bir xil.
"""
import argparse
import datetime as dt
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sun_times import sun_times, elevation_series, LAT, LON, TZ, CITY

# Firmware bilan bir xil parametrlar
ON_BELOW_PCT = 25.0     # shundan qorong'i bo'lsa -> yoqish
OFF_ABOVE_PCT = 40.0    # shundan yorug' bo'lsa -> o'chirish
CONFIRM_S = 60          # holat shuncha soniya turg'un bo'lsa almashadi
ALPHA = 0.2             # silliqlash koeffitsienti (1 soniyada 1 o'lchov)


def make_light(date, lat, lon, tz, seed):
    """Sensor ko'rsatishi (0-100 %) ni sun'iy yasash."""
    rng = np.random.default_rng(seed)
    t = np.arange(86400)
    elev = elevation_series(date, t, lat, lon, tz)
    ambient = np.clip((elev + 6) / 40.0, 0, 1) * 100       # -6 daraja -> 0 %, +34 -> 100 %

    c = np.zeros(86400)                                    # sekin o'zgaruvchi bulutlilik
    noise = rng.normal(size=86400)
    for i in range(1, 86400):
        c[i] = 0.9995 * c[i - 1] + 0.03 * noise[i]
    c = c / (c.std() + 1e-9)
    cloud = np.clip(0.8 + 0.15 * c, 0.4, 1.0)

    light = ambient * cloud + rng.normal(0, 1.0, 86400)    # sensor shovqini

    rise, sset = sun_times(date, lat, lon, tz)             # tunda mashina faralari
    night = [(0, int((rise.hour - 1) * 3600)), (int((sset.hour + 1) * 3600), 86000)]
    for _ in range(6):
        a, b = night[rng.integers(0, 2)]
        s = int(rng.integers(a, max(a + 1, b)))
        light[s:s + int(rng.integers(5, 20))] += 60
    return np.clip(light, 0, 100)


def run_smart(light):
    """Smart: silliqlash + gisterezis + tasdiqlash vaqti."""
    state, pending, level = False, 0, light[0]
    states, events = [], []
    for i, x in enumerate(light):
        level += ALPHA * (x - level)
        want = state
        if not state and level < ON_BELOW_PCT:
            want = True
        elif state and level > OFF_ABOVE_PCT:
            want = False
        if want != state:
            pending += 1
            if pending >= CONFIRM_S:
                state, pending = want, 0
                events.append((i, state))
        else:
            pending = 0
        states.append(state)
    return np.array(states), events


def run_naive(light, threshold=30.0):
    """Oddiy: bitta chegara, hech qanday himoyasiz."""
    states = light < threshold
    switches = int(np.sum(states[1:] != states[:-1]))
    return states, switches


def fmt(sec):
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--lat", type=float, default=LAT)
    ap.add_argument("--lon", type=float, default=LON)
    ap.add_argument("--tz", type=float, default=TZ)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    date = dt.date.fromisoformat(a.date)

    rise, sset = sun_times(date, a.lat, a.lon, a.tz)
    light = make_light(date, a.lat, a.lon, a.tz, a.seed)
    smart, events = run_smart(light)
    naive, naive_sw = run_naive(light)

    print(f"{CITY}, {date}")
    print(f"Quyosh chiqishi: {rise:%H:%M}   Quyosh botishi: {sset:%H:%M}\n")
    print("Smart boshqaruvchi almashishlari:")
    for i, on in events:
        print(f"  {fmt(i)}  ->  {'YONDI' if on else 'OCHDI'}")
    print(f"\nAlmashishlar soni: smart = {len(events)}, oddiy = {naive_sw}")

    os.makedirs("results", exist_ok=True)
    hours = np.arange(86400) / 3600
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(hours, light, lw=0.6, label="sensor (%)")
    ax[0].axhline(ON_BELOW_PCT, color="r", ls="--", label="yoqish chegarasi")
    ax[0].axhline(OFF_ABOVE_PCT, color="g", ls="--", label="o'chirish chegarasi")
    for t in (rise, sset):
        ax[0].axvline(t.hour + t.minute / 60, color="orange", ls=":")
    ax[0].set_ylabel("Yorug'lik, %")
    ax[0].legend(loc="upper right", fontsize=8)
    ax[1].step(hours, smart.astype(int) + 0.05, label=f"smart ({len(events)} almashish)")
    ax[1].step(hours, naive.astype(int) - 1.2, label=f"oddiy ({naive_sw} almashish)")
    ax[1].set_yticks([-1.2, 0.05, ]); ax[1].set_yticklabels(["oddiy", "smart"])
    ax[1].set_xlabel("Soat"); ax[1].set_xlim(0, 24)
    plt.tight_layout()
    plt.savefig("results/simulation.png", dpi=150)
    print("Grafik saqlandi: results/simulation.png")


if __name__ == "__main__":
    main()
