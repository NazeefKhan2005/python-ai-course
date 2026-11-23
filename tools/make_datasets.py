"""Generate the course datasets in site/data/: synthetic, seeded and byte-for-byte reproducible.

  python tools/make_datasets.py                # write every generated dataset into site/data/
  python tools/make_datasets.py shop sms       # only these datasets (names as in --list)
  python tools/make_datasets.py --list         # each dataset: its files, their size and shape, the lessons
  python tools/make_datasets.py --check        # exit 1 if site/data/ differs from a fresh run
  python tools/make_datasets.py --out DIR      # write into DIR instead of site/data/
  python tools/make_datasets.py --glove PATH   # also rebuild glove-mini.json from glove.6B.zip or glove.6B.50d.txt

Each dataset has its own generator, np.random.default_rng(seed), so changing one never changes another.
Values are formatted explicitly (fixed decimals, ISO 8601 dates, "\\n" line ends), and the SQLite and .npz
files are built in memory with fixed settings, so two runs give identical bytes. (--check compares SQLite
files by their SQL dump, because a database file's header records the SQLite version that wrote it.)
Each generator also asserts the patterns its lessons rely on (a unique busiest hour, a Simpson's paradox,
a fall in repeat orders, ...): if an edit breaks one, the run fails here instead of in a lesson. The
docstrings say what is planted; site/data/README.md, which learners read, describes only the columns.

Everything is fictional: names come from many cultures (spec/06 §11), amounts are in a generic currency,
units are metric, and times are 24-hour local times. Two parts of site/data/ are not generated from seeds:
docs/ (the company handbook, written by hand) and glove-mini.json (a subset of the public-domain GloVe
vectors, rebuilt only with --glove).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sqlite3
import sys
import zipfile
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
MAX_BYTES = 2_000_000             # spec/03 §9: at most 2 MB per file
STAMP = (2026, 1, 1, 0, 0, 0)     # fixed zip timestamp, as in export_exercises.py
NOT_GENERATED = ("README.md", "glove-mini.json", "docs")
Files = dict[str, bytes]
Rng = np.random.Generator


# ----------------------------------------------------------------------------- writers
def csv_bytes(header: Sequence[str], rows: Iterable[Sequence[object]]) -> bytes:
    """A header row, then the rows; "\\n" line ends, minimal quoting, None written as an empty field."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def text_bytes(lines: Iterable[str]) -> bytes:
    return "".join(f"{line}\n" for line in lines).encode("utf-8")


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sqlite_bytes(schema: str, tables: dict[str, tuple[Sequence[str], Sequence[Sequence[object]]]]) -> bytes:
    """Create the tables in an in-memory database, insert the rows, VACUUM, and return the file image."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(schema)
        for table, (columns, rows) in tables.items():
            marks = ", ".join("?" * len(columns))
            conn.executemany(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({marks})", rows)
        conn.commit()
        conn.execute("VACUUM")
        return conn.serialize()
    finally:
        conn.close()


def sqlite_dump(image: bytes) -> str:
    """The SQL text of a database file image: equal dumps mean equal schemas and rows."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.deserialize(image)
        return "\n".join(conn.iterdump())
    finally:
        conn.close()


def npz_bytes(arrays: dict[str, np.ndarray]) -> bytes:
    """An uncompressed .npz (the format np.savez writes) with sorted names and a fixed timestamp."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        for name in sorted(arrays):
            member = io.BytesIO()
            np.lib.format.write_array(member, np.ascontiguousarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", STAMP)
            info.external_attr = 0o644 << 16
            zf.writestr(info, member.getvalue())
    return buffer.getvalue()


def f1(x: float) -> str:
    return f"{x:.1f}"


def f2(x: float) -> str:
    return f"{x:.2f}"


def stamp(t: datetime) -> str:
    return t.strftime("%Y-%m-%d %H:%M:%S")


def yes_no(flag: object) -> str:
    return "yes" if flag else "no"


def pick(rng: Rng, options: Sequence[str], n: int, p: Sequence[float] | None = None) -> list[str]:
    """n draws from options, as Python strings."""
    weights = None if p is None else np.asarray(p, float) / np.sum(p)
    return [options[i] for i in rng.choice(len(options), n, p=weights)]


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def shift_to_rate(logit: np.ndarray, rate: float) -> float:
    """The constant that, added to logit, makes the mean probability equal rate (bisection)."""
    low, high = -20.0, 20.0
    for _ in range(80):
        middle = (low + high) / 2
        if sigmoid(logit + middle).mean() > rate:
            high = middle
        else:
            low = middle
    return (low + high) / 2


# ----------------------------------------------------------------------------- people
FIRST_NAMES = (
    "Aisyah", "Ben", "Chen", "Dev", "Fatima", "Kofi", "Lucía", "Mei", "Omar", "Priya", "Tomás", "Yuki",
    "Abebe", "Ama", "Amara", "Ana", "Andrei", "Anika", "Arjun", "Aylin", "Bilal", "Bongani", "Camila",
    "Carlos", "Chidi", "Chloé", "Daniel", "Dara", "Diego", "Dmitri", "Elif", "Emeka", "Emma", "Esra",
    "Farah", "Felipe", "Femi", "Grace", "Hamza", "Hana", "Hiroshi", "Hugo", "Ibrahim", "Ikram", "Inês",
    "Isabela", "Ivan", "Jamal", "Javier", "Ji-woo", "Jin", "Joon", "Kai", "Kavya", "Kenji", "Khalid",
    "Lars", "Layla", "Leila", "Lerato", "Liam", "Lina", "Luca", "Malik", "Mariam", "Marta", "Mateo",
    "Maya", "Mehmet", "Minh", "Musa", "Nadia", "Naledi", "Nia", "Nikhil", "Nina", "Noah", "Nour", "Olga",
    "Oluwaseun", "Oscar", "Pablo", "Paulo", "Quang", "Rahul", "Rania", "Ravi", "Rin", "Rosa", "Sakura",
    "Samir", "Sana", "Santiago", "Sara", "Siddharth", "Sipho", "Sofia", "Soo-ah", "Sunil", "Tariq",
    "Thabo", "Thandiwe", "Tunde", "Uma", "Valentina", "Vikram", "Wanjiru", "Wei", "Xavier", "Xin", "Yara",
    "Yasmin", "Yaw", "Yusuf", "Zainab", "Zara", "Zeynep", "Zoe",
)
LAST_NAMES = (
    "Abdullah", "Adeyemi", "Ahmed", "Akhtar", "Alvarez", "Andersen", "Asante", "Banda", "Bekele",
    "Bianchi", "Boateng", "Chen", "Cohen", "Costa", "Das", "Demir", "Diallo", "Dimitrov", "Dubois", "Eze",
    "Farouk", "Fernandes", "Fischer", "Garcia", "Gonzalez", "Gupta", "Haddad", "Haile", "Hashemi", "Hassan",
    "Hernández", "Hoang", "Horvat", "Huang", "Ibrahim", "Ito", "Iyer", "Jensen", "Kamau", "Kaplan", "Kaya",
    "Khan", "Kim", "Korhonen", "Kowalski", "Kumar", "Lee", "Li", "Lim", "Lindqvist", "Lopez", "Mahlangu",
    "Martin", "Mendes", "Mensah", "Moreau", "Morales", "Mukherjee", "Müller", "Musa", "Mwangi",
    "Nakamura", "Nasser", "Nguyen", "Njoroge", "Novak", "Nowak", "Obi", "Odhiambo", "Okafor", "Okeke",
    "Olsen", "Ortiz", "Osei", "Owusu", "Öztürk", "Park", "Patel", "Pereira", "Petrov", "Popescu", "Qureshi",
    "Rahman", "Ramos", "Rao", "Reyes", "Rossi", "Saito", "Salazar", "Santos", "Sato", "Schmidt", "Shah",
    "Silva", "Singh", "Sørensen", "Suzuki", "Tanaka", "Tesfaye", "Tran", "Tshabalala", "Usman", "Vargas",
    "Wang", "Wanjiku", "Wu", "Yamamoto", "Yildiz", "Yusuf", "Zhang", "Zulu",
)


def unique_names(rng: Rng, n: int) -> list[str]:
    """n different "First Last" names."""
    names: list[str] = []
    seen: set[str] = set()
    while len(names) < n:
        first, last = rng.integers(len(FIRST_NAMES)), rng.integers(len(LAST_NAMES))
        name = f"{FIRST_NAMES[first]} {LAST_NAMES[last]}"
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


# ----------------------------------------------------------------------------- server logs
LOG_HOURS = np.array([3, 2, 2, 2, 2, 3, 5, 9, 14, 16, 17, 19, 23, 30, 21, 18, 17, 18, 21, 24, 22, 16, 10, 6], float)
LOG_SHARE = LOG_HOURS / LOG_HOURS.sum()
LOG_TEMPLATES = {  # level -> (weight, message template)
    "DEBUG": ((3, "Cache hit for product:{product}"), (2, "Query took {ms} ms"), (1, "Opening database connection")),
    "INFO": ((30, "User u{user} logged in"), (12, "User u{user} logged out"), (25, "GET /api/{endpoint} 200 {ms} ms"),
             (8, "POST /api/orders 201 {ms} ms"), (10, "Order {order} created"), (6, "Payment {payment} authorised"),
             (3, "Cache refreshed ({keys} keys)"), (5, "Email sent to u{user}")),
    "WARNING": ((5, "Slow response from payment service ({slow} ms)"),
                (3, "Retrying database connection (attempt {attempt})"),
                (3, "High memory usage: {pct}%"), (2, "Rate limit reached for client c{client}")),
}
ENDPOINTS = ("orders", "products", "search", "cart", "users", "reviews")
TRACEBACKS = {
    "Database connection lost": (
        "  Traceback (most recent call last):",
        '    File "app/db.py", line 142, in execute',
        "      cursor.execute(sql, params)",
        "  ConnectionError: server closed the connection unexpectedly"),
    "Payment service timeout": (
        "  Traceback (most recent call last):",
        '    File "app/payments.py", line 88, in charge',
        "      response = client.post(url, json=payload, timeout=5)",
        "  TimeoutError: the payment service did not answer within 5 s"),
}
Event = tuple[datetime, str, str]


def log_messages(rng: Rng, level: str, n: int) -> list[str]:
    weights, templates = zip(*LOG_TEMPLATES[level], strict=True)
    chosen = rng.choice(len(templates), n, p=np.array(weights, float) / sum(weights))
    fields = {
        "user": rng.integers(1001, 1800, n), "ms": np.round(rng.lognormal(4.2, 0.6, n)).astype(int),
        "slow": rng.integers(1500, 9000, n), "order": rng.integers(100_000, 1_000_000, n),
        "payment": rng.integers(500_000, 1_000_000, n), "keys": rng.integers(800, 5000, n),
        "product": rng.integers(1, 500, n), "attempt": rng.integers(2, 5, n), "pct": rng.integers(86, 98, n),
        "client": rng.integers(10, 99, n), "endpoint": rng.choice(ENDPOINTS, n)}
    return [templates[k].format(**{key: values[i] for key, values in fields.items()}) for i, k in enumerate(chosen)]


def log_day(rng: Rng, day: datetime, volume: float) -> list[Event]:
    """Routine DEBUG, INFO and WARNING lines for one day, following the hourly traffic shape."""
    counts = rng.poisson(volume * LOG_SHARE)
    seconds = np.concatenate([np.sort(rng.integers(h * 3600, (h + 1) * 3600, c)) for h, c in enumerate(counts)])
    levels = rng.choice(np.array(["DEBUG", "INFO", "WARNING"]), seconds.size, p=[0.04, 0.85, 0.11])
    events = []
    for level in ("DEBUG", "INFO", "WARNING"):
        where = np.flatnonzero(levels == level)
        for i, message in zip(where, log_messages(rng, level, where.size), strict=True):
            events.append((day + timedelta(seconds=int(seconds[i])), level, message))
    return events


def at_times(rng: Rng, day: datetime, n: int, start: float, end: float, level: str, message: str) -> list[Event]:
    """n lines between two hours of the day (fractions allowed: 13.25 is 13:15)."""
    seconds = np.sort(rng.integers(int(start * 3600), int(end * 3600), n))
    return [(day + timedelta(seconds=int(s)), level, message) for s in seconds]


def with_traffic(rng: Rng, day: datetime, n: int, level: str, message: str) -> list[Event]:
    """n lines spread over the day like the traffic."""
    seconds = np.sort(rng.choice(24, n, p=LOG_SHARE) * 3600 + rng.integers(0, 3600, n))
    return [(day + timedelta(seconds=int(s)), level, message) for s in seconds]


def disk_warnings(rng: Rng, day: datetime, start: float, end: float) -> list[Event]:
    times = at_times(rng, day, 8, start, end, "WARNING", "")
    return [(t, "WARNING", f"Disk usage at {pct}%") for (t, _, _), pct in zip(times, range(86, 102, 2), strict=True)]


def format_events(events: list[Event]) -> list[str]:
    return [f"{stamp(t)} [{level}] {message}" for t, level, message in sorted(events, key=lambda e: e[0])]


def make_server_logs(rng: Rng) -> Files:
    """M05 project: one day (2026-03-01) of logs from an online shop's API server, one record per line.

    Planted: the busiest hour is 13:00-13:59, at least 10 lines ahead of the next. ERROR messages are fixed
    strings; the top three are "Database connection lost" (34), "Payment service timeout" (26) and "Disk
    full" (17), then "Failed to send email" (11). Disk-usage warnings at 02:30-03:05 lead to the disk-full
    errors at 03:05-03:45; a database incident at 13:10-13:25 brings 20 database errors and 3 CRITICAL lines.
    """
    day = datetime(2026, 3, 1)
    events = log_day(rng, day, 1500)
    events += disk_warnings(rng, day, 2.5, 3.08)
    events += at_times(rng, day, 17, 3.08, 3.75, "ERROR", "Disk full")
    events += at_times(rng, day, 20, 13.17, 13.42, "ERROR", "Database connection lost")
    events += with_traffic(rng, day, 14, "ERROR", "Database connection lost")
    events += at_times(rng, day, 3, 13.2, 13.33, "CRITICAL", "Service unavailable")
    for message, n in (("Payment service timeout", 26), ("Failed to send email", 11),
                       ("Invalid session token", 8), ("Image upload failed", 5)):
        events += with_traffic(rng, day, n, "ERROR", message)
    hours = Counter(t.hour for t, _, _ in events).most_common(2)
    assert hours[0][0] == 13 and hours[0][1] - hours[1][1] >= 10, hours
    errors = Counter(message for _, level, message in events if level == "ERROR").most_common(4)
    assert [n for _, n in errors] == [34, 26, 17, 11], errors
    return {"server_logs.txt": text_bytes(format_events(events))}


def make_server_logs_large(rng: Rng) -> Files:
    """M08 project: a week of logs (2026-03-02 to 2026-03-08) for a streaming pipeline.

    The same record format as server_logs.txt, plus what real logs contain: about half of the database and
    payment errors are followed by an indented traceback (continuation lines that start with two spaces), and
    6 lines were cut off when the log writer crashed. Weekends are quieter. Incidents: 60 database errors and
    4 CRITICAL lines on 2026-03-04 14:05-14:40; disk-usage warnings, then 25 disk-full errors, on 2026-03-06
    from 02:20.
    """
    events: list[Event] = []
    for k in range(7):
        day = datetime(2026, 3, 2) + timedelta(days=k)
        events += log_day(rng, day, 3300 * (0.8 if day.weekday() >= 5 else 1.0))
        for message, mean in (("Payment service timeout", 12), ("Database connection lost", 5),
                              ("Failed to send email", 4), ("Invalid session token", 6), ("Image upload failed", 2)):
            events += with_traffic(rng, day, int(rng.poisson(mean)), "ERROR", message)
        if k == 2:
            events += at_times(rng, day, 60, 14.08, 14.67, "ERROR", "Database connection lost")
            events += at_times(rng, day, 4, 14.17, 14.5, "CRITICAL", "Service unavailable")
        if k == 4:
            events += disk_warnings(rng, day, 2.33, 3.0)
            events += at_times(rng, day, 25, 3.0, 3.67, "ERROR", "Disk full")
    lines = []
    for line in format_events(events):
        lines.append(line)
        message = line.split("] ", 1)[1]
        if message in TRACEBACKS and rng.random() < 0.5:
            lines.extend(TRACEBACKS[message])
    info = [i for i, line in enumerate(lines) if "[INFO]" in line]
    for i in sorted(rng.choice(info, 6, replace=False)):
        lines[i] = lines[i][: int(rng.integers(8, len(lines[i]) - 4))]
    assert sum(line.startswith("  ") for line in lines) > 100
    return {"server_logs_large.txt": text_bytes(lines)}


# ----------------------------------------------------------------------------- images
def make_images(rng: Rng) -> Files:
    """M11 project (and elective E2): six small images as uint8 arrays.

    landscape, shapes and noisy_shapes are RGB, shape (120, 160, 3); checkerboard (128, 128), gradient
    (64, 256) and cells (128, 128) are grayscale. shapes has flat colours and sharp edges (Sobel, threshold);
    noisy_shapes is shapes plus Gaussian noise with sigma 30 (box blur); gradient is a 0-255 ramp
    (brightness); cells has 24 separate bright blobs on a dark background (threshold, counting objects).
    """
    h, w = 120, 160
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    t = (yy / (h - 1))[..., None]
    img = (1 - t) * np.array([70.0, 130, 210]) + t * np.array([200.0, 225, 245])
    sun = np.clip(14.5 - np.hypot(yy - 30, xx - 118), 0, 1)[..., None]
    img = img * (1 - sun) + sun * np.array([250.0, 215, 90])
    x = np.arange(w)
    far = 62 + 10 * np.sin(x / 17) + 6 * np.sin(x / 7 + 1.3) + np.cumsum(rng.normal(0, 0.6, w))
    near = 84 + 7 * np.sin(x / 23 + 2) + 4 * np.sin(x / 5) + np.cumsum(rng.normal(0, 0.4, w))
    img[yy > far] = (110, 118, 140)
    img[yy > near] = (64, 112, 70)
    img[yy > 102] = (86, 150, 64)
    landscape = np.clip(np.round(img + rng.normal(0, 4, img.shape)), 0, 255).astype(np.uint8)

    img = np.full((h, w, 3), 235.0)
    img[np.hypot(yy - 42, xx - 42) <= 24] = (220, 50, 47)
    img[(yy >= 72) & (yy < 108) & (xx >= 18) & (xx < 74)] = (38, 84, 200)
    img[(yy >= 18) & (yy < 70) & (np.abs(xx - 118) <= (yy - 18) * 0.6)] = (46, 160, 67)
    ring = np.hypot(yy - 94, xx - 122)
    img[(ring >= 12) & (ring <= 19)] = (20, 20, 20)
    shapes = img.astype(np.uint8)
    noisy = np.clip(np.round(img + rng.normal(0, 30, img.shape)), 0, 255).astype(np.uint8)

    i, j = np.mgrid[0:128, 0:128]
    checkerboard = np.where((i // 16 + j // 16) % 2 == 0, 225, 30).astype(np.uint8)
    gradient = np.tile(np.arange(256, dtype=np.uint8), (64, 1))
    canvas = np.full((128, 128), 18.0)
    centres: list[np.ndarray] = []
    while len(centres) < 24:
        c = rng.uniform(9, 119, 2)
        if all(np.hypot(*(c - p)) > 15 for p in centres):
            centres.append(c)
    for cy, cx in centres:
        s, a = rng.uniform(2.5, 4.5), rng.uniform(150, 220)
        canvas += a * np.exp(-((i - cy) ** 2 + (j - cx) ** 2) / (2 * s * s))
    cells = np.clip(np.round(canvas + rng.normal(0, 8, canvas.shape)), 0, 255).astype(np.uint8)
    arrays = {"landscape": landscape, "shapes": shapes, "noisy_shapes": noisy, "checkerboard": checkerboard,
              "gradient": gradient, "cells": cells}
    return {"images.npz": npz_bytes(arrays)}


# ----------------------------------------------------------------------------- the online shop
REGIONS = {
    "Africa": ("Lagos", "Nairobi", "Accra", "Cairo", "Johannesburg", "Casablanca"),
    "Americas": ("São Paulo", "Mexico City", "Toronto", "Bogotá", "Lima", "Chicago"),
    "Asia-Pacific": ("Jakarta", "Mumbai", "Manila", "Tokyo", "Seoul", "Sydney", "Kuala Lumpur", "Dhaka"),
    "Europe": ("Berlin", "Madrid", "Warsaw", "Istanbul", "Lisbon", "Stockholm", "Paris"),
}
COUNTRIES = {
    "Lagos": "Nigeria", "Nairobi": "Kenya", "Accra": "Ghana", "Cairo": "Egypt", "Johannesburg": "South Africa",
    "Casablanca": "Morocco", "São Paulo": "Brazil", "Mexico City": "Mexico", "Toronto": "Canada",
    "Bogotá": "Colombia", "Lima": "Peru", "Chicago": "United States", "Jakarta": "Indonesia", "Mumbai": "India",
    "Manila": "Philippines", "Tokyo": "Japan", "Seoul": "South Korea", "Sydney": "Australia",
    "Kuala Lumpur": "Malaysia", "Dhaka": "Bangladesh", "Berlin": "Germany", "Madrid": "Spain",
    "Warsaw": "Poland", "Istanbul": "Türkiye", "Lisbon": "Portugal", "Stockholm": "Sweden", "Paris": "France",
}
PRODUCTS = (  # name, category, unit price
    ("Wireless earbuds", "Electronics", 59.90), ("Smartwatch", "Electronics", 149.00),
    ("Bluetooth speaker", "Electronics", 45.50), ("Phone charger", "Electronics", 19.90),
    ("Laptop stand", "Electronics", 34.00), ("USB-C hub", "Electronics", 29.90),
    ("Mechanical keyboard", "Electronics", 89.00), ("Webcam", "Electronics", 54.00),
    ("Coffee grinder", "Home & Kitchen", 39.00), ("Chef's knife", "Home & Kitchen", 49.50),
    ("Non-stick pan", "Home & Kitchen", 32.00), ("Desk lamp", "Home & Kitchen", 27.90),
    ("Storage boxes (set of 3)", "Home & Kitchen", 18.50), ("Water filter jug", "Home & Kitchen", 24.90),
    ("Cotton bedsheet set", "Home & Kitchen", 44.00), ("Electric kettle", "Home & Kitchen", 29.00),
    ("Data Stories", "Books", 22.00), ("The World Cookbook", "Books", 28.00),
    ("Mystery at Blue Lake", "Books", 12.90), ("Statistics Made Simple", "Books", 26.50),
    ("Atlas of Rivers", "Books", 35.00), ("Poems for Mornings", "Books", 11.50),
    ("A Short History of Trade", "Books", 19.90), ("Kids' Science Lab", "Books", 15.00),
    ("Cotton T-shirt", "Clothing", 14.90), ("Hoodie", "Clothing", 39.90), ("Running shoes", "Clothing", 79.00),
    ("Rain jacket", "Clothing", 64.00), ("Wool socks (3 pairs)", "Clothing", 16.50),
    ("Denim jeans", "Clothing", 49.00), ("Sun hat", "Clothing", 17.90), ("Canvas backpack", "Clothing", 42.00),
    ("Yoga mat", "Sports", 24.00), ("Dumbbell set", "Sports", 59.00), ("Steel water bottle", "Sports", 18.00),
    ("Resistance bands", "Sports", 15.90), ("Football", "Sports", 21.00), ("Tennis racket", "Sports", 69.00),
    ("Bike helmet", "Sports", 45.00), ("Skipping rope", "Sports", 8.90),
    ("Sunscreen SPF 50", "Beauty & Health", 13.90), ("Face cream", "Beauty & Health", 21.50),
    ("Shampoo", "Beauty & Health", 8.90), ("Electric toothbrush", "Beauty & Health", 39.00),
    ("Hand cream", "Beauty & Health", 7.50), ("Vitamin C tablets", "Beauty & Health", 11.00),
    ("Hair dryer", "Beauty & Health", 34.90), ("Lip balm", "Beauty & Health", 4.50),
)
CATEGORY_MIX = {
    "consumer": {"Electronics": 0.17, "Home & Kitchen": 0.17, "Books": 0.14, "Clothing": 0.24, "Sports": 0.14,
                 "Beauty & Health": 0.14},
    "business": {"Electronics": 0.42, "Home & Kitchen": 0.30, "Books": 0.10, "Clothing": 0.04, "Sports": 0.04,
                 "Beauty & Health": 0.10},
}
REGION_TREND = {"Africa": (0.6, 1.6), "Americas": (1.25, 0.75), "Asia-Pacific": (0.8, 1.3), "Europe": (1.0, 1.0)}
SHOP_SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT NOT NULL,
    country     TEXT NOT NULL,
    region      TEXT NOT NULL,
    segment     TEXT NOT NULL CHECK (segment IN ('consumer', 'business')),
    signup_date TEXT NOT NULL,
    referred_by INTEGER REFERENCES customers (customer_id)
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    category   TEXT NOT NULL,
    unit_price REAL NOT NULL,
    unit_cost  REAL NOT NULL
);
CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date  TEXT NOT NULL,
    channel     TEXT,
    status      TEXT NOT NULL CHECK (status IN ('delivered', 'returned', 'cancelled'))
);
CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL,
    discount   REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, product_id)
);
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    department  TEXT NOT NULL,
    job_title   TEXT NOT NULL,
    manager_id  INTEGER REFERENCES employees (employee_id),
    hire_date   TEXT NOT NULL,
    salary      INTEGER NOT NULL
);
"""
STAFF = (  # department, number of staff per job title (title, count, lowest salary, highest salary)
    ("Engineering", (("Software engineer", 6, 62_000, 86_000), ("Data engineer", 2, 66_000, 82_000))),
    ("Sales", (("Account manager", 5, 48_000, 64_000),)),
    ("Marketing", (("Marketing specialist", 3, 46_000, 60_000), ("Data analyst", 1, 52_000, 58_000))),
    ("Customer Support", (("Support agent", 7, 34_000, 42_000), ("Support team lead", 1, 47_000, 50_000))),
    ("Operations", (("Warehouse coordinator", 4, 38_000, 48_000), ("Logistics planner", 2, 50_000, 58_000))),
    ("Finance", (("Accountant", 2, 52_000, 64_000), ("Financial analyst", 1, 58_000, 66_000))),
)


def shop_employees(rng: Rng, names: list[str]) -> list[tuple]:
    """CEO -> department heads -> staff; in Engineering, two leads sit between the head and the engineers."""
    rows: list[tuple] = [(1, names[0], "Management", "Chief executive officer", None, "2019-02-01", 165_000)]

    def hired(low: int, high: int) -> str:
        return (date(low, 1, 1) + timedelta(days=int(rng.integers(0, (high - low + 1) * 365)))).isoformat()

    for department, titles in STAFF:
        head = len(rows) + 1
        salary = int(rng.integers(220, 261)) * 500
        rows.append((head, names[head - 1], department, f"Head of {department}", 1, hired(2019, 2021), salary))
        managers = [head]
        if department == "Engineering":
            for k in range(2):
                rows.append((len(rows) + 1, names[len(rows)], department, "Engineering lead", head,
                             hired(2020, 2022), 104_000))   # equal salaries: RANK vs DENSE_RANK
                managers.append(len(rows))
        for title, count, low, high in titles:
            for k in range(count):
                manager = managers[1 + k % 2] if department == "Engineering" else head
                pay = int(rng.integers(low // 500, high // 500 + 1)) * 500
                rows.append((len(rows) + 1, names[len(rows)], department, title, manager, hired(2020, 2025), pay))
    agents = [i for i, row in enumerate(rows) if row[3] == "Support agent"]
    top = max(rows[i][6] for i in agents)
    second = sorted(agents, key=lambda i: rows[i][6])[-2]
    rows[second] = (*rows[second][:6], top)       # two agents share the top agent salary
    return rows


def make_shop(rng: Rng) -> Files:
    """M12, M13 and M15: an online shop's 2025 sales as CSV exports and as a SQLite database.

    One universe, three files: customers.csv (the customers table), sales.csv (one row per product line of
    every delivered 2025 order, with the customer's region and city) and shop.db (customers, products,
    orders of every status, order_items and employees). Planted: seasonality (a July sale, a peak on
    2025-11-28 and December), regional trends (demand per customer rises through the year in Africa, fastest,
    and Asia-Pacific, holds in Europe and falls in the Americas), channel missing for orders placed during a tracking outage (2025-01-02 to 2025-01-09),
    15 deleted customer accounts whose orders remain (unmatched rows in merges and LEFT JOINs), referrals
    (a self-join), and two pairs of equal salaries in employees.
    """
    n_customers = 2000
    n_staff = 1 + sum(1 + sum(c for _, c, _, _ in titles) + 2 * (d == "Engineering") for d, titles in STAFF)
    names = unique_names(rng, n_customers + n_staff)
    staff_names, customer_names = names[:n_staff], names[n_staff:]
    regions = pick(rng, list(REGIONS), n_customers, [0.18, 0.22, 0.34, 0.26])
    cities = [REGIONS[r][int(rng.integers(len(REGIONS[r])))] for r in regions]
    segments = pick(rng, ["consumer", "business"], n_customers, [0.85, 0.15])
    first_day, span = date(2022, 1, 3), (date(2025, 12, 20) - date(2022, 1, 3)).days
    signups = sorted(first_day + timedelta(days=int(x * span)) for x in rng.power(1.8, n_customers))
    customers = []
    for k in range(n_customers):
        referred = 1001 + int(rng.integers(0, k)) if k > 20 and rng.random() < 0.15 else None
        customers.append([1001 + k, customer_names[k], cities[k], COUNTRIES[cities[k]], regions[k], segments[k],
                          signups[k].isoformat(), referred])

    days = [date(2025, 1, 1) + timedelta(days=k) for k in range(365)]
    season = np.array([0.9, 0.8, 0.95, 1.0, 1.0, 1.05, 1.2, 0.95, 1.0, 1.05, 1.45, 1.35])[[d.month - 1 for d in days]]
    for k, d in enumerate(days):
        if date(2025, 7, 10) <= d <= date(2025, 7, 16):
            season[k] *= 1.8
        if d == date(2025, 11, 28):
            season[k] *= 4.0
        elif date(2025, 11, 29) <= d <= date(2025, 12, 1):
            season[k] *= 2.0
    week = {"consumer": np.array([1.0, 1.0, 1.0, 1.05, 1.1, 1.25, 1.2]),
            "business": np.array([1.25, 1.25, 1.25, 1.2, 1.1, 0.3, 0.2])}
    weekday = np.array([d.weekday() for d in days])
    progress = np.arange(365) / 364
    weights = {(r, s): season * week[s][weekday] * (a + (b - a) * progress)
               for r, (a, b) in REGION_TREND.items() for s in week}
    names_by_category = defaultdict(list)
    for p, (_, category, _) in enumerate(PRODUCTS):
        names_by_category[category].append(p)
    popularity = rng.gamma(2.0, 1.0, len(PRODUCTS))
    product_p = {}
    for segment, mix in CATEGORY_MIX.items():
        p = np.array([mix[c] * popularity[i] / sum(popularity[j] for j in names_by_category[c])
                      for i, (_, c, _) in enumerate(PRODUCTS)])
        product_p[segment] = p / p.sum()

    orders = []        # [customer_id, date, channel, status, [(product, quantity, discount)]]
    for cid, _, _, _, region, segment, signup, _ in customers:
        start = max(0, (date.fromisoformat(signup) - days[0]).days)
        if start >= 365:
            continue
        w = weights[region, segment][start:]
        rate = rng.gamma(2.0, 1.4) if segment == "consumer" else rng.gamma(3.0, 3.0)
        for day_index in sorted(start + rng.choice(w.size, rng.poisson(rate * w.sum() / 365), p=w / w.sum())):
            d = days[day_index]
            if segment == "consumer":
                n_lines = int(rng.choice([1, 2, 3, 4], p=[0.6, 0.28, 0.09, 0.03]))
                channel = pick(rng, ["app", "web"], 1, [0.55, 0.45])[0]
            else:
                n_lines = int(rng.choice([1, 2, 3, 4, 5], p=[0.35, 0.3, 0.18, 0.1, 0.07]))
                channel = pick(rng, ["web", "phone", "app"], 1, [0.7, 0.2, 0.1])[0]
            if date(2025, 1, 2) <= d <= date(2025, 1, 9):
                channel = None
            if date(2025, 7, 10) <= d <= date(2025, 7, 16):
                order_discount = 0.15
            elif date(2025, 11, 28) <= d <= date(2025, 12, 1):
                order_discount = 0.20
            else:
                order_discount = 0.10 if rng.random() < 0.08 else 0.0
            lines = []
            for p in rng.choice(len(PRODUCTS), n_lines, replace=False, p=product_p[segment]):
                if segment == "consumer":
                    quantity = int(rng.choice([1, 2, 3], p=[0.8, 0.15, 0.05]))
                else:
                    quantity = int(min(24, rng.geometric(0.22)))
                discount = order_discount or (0.05 if quantity >= 10 else 0.0)
                lines.append((int(p), quantity, discount))
            clothing = any(PRODUCTS[p][1] == "Clothing" for p, _, _ in lines)
            status = pick(rng, ["delivered", "returned", "cancelled"], 1,
                          [0.93 - 0.06 * clothing, 0.04 + 0.06 * clothing, 0.03])[0]
            orders.append([cid, d, channel, status, lines])
    orders.sort(key=lambda o: (o[1], o[0]))

    buyers = sorted({o[0] for o in orders if o[3] == "delivered"} - {c[7] for c in customers if c[7]})
    consumers = {c[0] for c in customers if c[5] == "consumer"}
    deleted = set(rng.choice([b for b in buyers if b in consumers], 15, replace=False).tolist())
    by_id = {c[0]: c for c in customers}
    kept = [c for c in customers if c[0] not in deleted]

    sales, order_rows, item_rows = [], [], []
    for k, (cid, d, channel, status, lines) in enumerate(orders):
        oid = 250_001 + k
        order_rows.append((oid, cid, d.isoformat(), channel, status))
        _, _, city, country, region, _, _, _ = by_id[cid]
        for p, quantity, discount in lines:
            name, category, price = PRODUCTS[p]
            item_rows.append((oid, p + 1, quantity, price, discount))
            if status == "delivered":
                revenue = round(quantity * price * (1 - discount) + 1e-9, 2)
                sales.append((oid, d.isoformat(), cid, region, country, city, channel, category, name, quantity,
                              f2(price), f2(discount), f2(revenue)))
    costs = rng.uniform(0.45, 0.7, len(PRODUCTS))
    product_rows = [(p + 1, name, category, price, round(price * costs[p], 2))
                    for p, (name, category, price) in enumerate(PRODUCTS)]
    employees = shop_employees(rng, staff_names)

    revenue = defaultdict(float)
    for row in sales:
        revenue[row[3], int(row[1][5:7]) <= 6] += float(row[12])
    growth = {r: revenue[r, False] / revenue[r, True] for r in REGIONS}
    assert growth["Africa"] > growth["Asia-Pacific"] > growth["Europe"] > growth["Americas"], growth
    by_month = Counter(row[1][5:7] for row in sales)
    assert by_month.most_common(1)[0][0] == "11", by_month
    assert {row[2] for row in sales} - {c[0] for c in kept} == deleted
    assert {row[1][:10] for row in sales if row[6] is None} <= {f"2025-01-{d:02d}" for d in range(2, 10)}
    assert len({row[6] for row in employees}) < len(employees)

    customer_header = ("customer_id", "name", "city", "country", "region", "segment", "signup_date", "referred_by")
    return {
        "customers.csv": csv_bytes(customer_header, kept),
        "sales.csv": csv_bytes(("order_id", "order_date", "customer_id", "region", "country", "city", "channel",
                                "category", "product", "quantity", "unit_price", "discount", "revenue"), sales),
        "shop.db": sqlite_bytes(SHOP_SCHEMA, {
            "customers": (customer_header, kept),
            "products": (("product_id", "name", "category", "unit_price", "unit_cost"), product_rows),
            "orders": (("order_id", "customer_id", "order_date", "channel", "status"), order_rows),
            "order_items": (("order_id", "product_id", "quantity", "unit_price", "discount"), item_rows),
            "employees": (("employee_id", "name", "department", "job_title", "manager_id", "hire_date", "salary"),
                          employees)}),
    }


# ----------------------------------------------------------------------------- food delivery
FD_CITIES = {"Bogotá": 0.34, "Lima": 0.28, "Medellín": 0.16, "Cali": 0.11, "Quito": 0.11}
FD_TRAFFIC = {"Bogotá": 1.15, "Lima": 1.10, "Medellín": 1.0, "Cali": 0.95, "Quito": 1.0}
FD_RESTAURANTS = {"Bogotá": 50, "Lima": 42, "Medellín": 24, "Cali": 17, "Quito": 17}
NEIGHBOURHOODS = {
    "Bogotá": ("Chapinero", "Usaquén", "Teusaquillo", "Suba", "Kennedy", "Fontibón", "La Candelaria", "Engativá"),
    "Lima": ("Miraflores", "Barranco", "San Isidro", "Surco", "Lince", "San Borja", "Jesús María", "La Molina"),
    "Medellín": ("El Poblado", "Laureles", "Envigado", "Belén", "Robledo"),
    "Cali": ("Granada", "San Fernando", "Ciudad Jardín", "El Peñón"),
    "Quito": ("La Mariscal", "Cumbayá", "La Floresta", "El Batán"),
}
CUISINES = {  # cuisine: (price level, restaurant names)
    "Colombian": (1, ("La Fonda", "El Fogón", "Casa de la Arepa", "Sabor de Casa", "La Cazuela")),
    "Peruvian": (2, ("El Rincón Criollo", "Cevichería del Puerto", "La Causa", "Sabor Norteño")),
    "Ecuadorian": (1, ("El Encebollado", "Hornado de la Esquina", "Sabor Andino")),
    "Pizza": (2, ("Pizza Forno", "Napoli Express", "Slice House", "La Masa")),
    "Burgers": (2, ("Burger Barrio", "Smash Point", "Brasa Burgers", "Bun & Grill")),
    "Chicken": (1, ("Pollo Dorado", "Brasa Real", "Wings Corner")),
    "Chinese": (2, ("Chifa Dragón Dorado", "Wok Express", "Jade Garden")),
    "Japanese": (3, ("Sushi Nami", "Ramen Kaze", "Maki House")),
    "Mexican": (2, ("Taquería La Lupita", "El Burrito Feliz", "Cantina Maíz")),
    "Middle Eastern": (2, ("Falafel Yalla", "Shawarma Hamsa", "Cedro Grill")),
    "Indian": (2, ("Tandoor House", "Curry Leaf", "Masala Corner")),
    "Vegetarian": (2, ("Green Bowl", "La Huerta", "Raíz Kitchen")),
    "Seafood": (3, ("Mar Adentro", "La Red", "Pesca del Día")),
    "Desserts": (1, ("Dulce Antojo", "Helados Nube", "Brownie Lab")),
    "Bakery & Coffee": (1, ("Café Altura", "Pan de Casa", "Tostado Coffee")),
}
LOCAL_CUISINE = {"Bogotá": {"Colombian": 4}, "Medellín": {"Colombian": 4}, "Cali": {"Colombian": 4},
                 "Lima": {"Peruvian": 4, "Chinese": 2.5, "Seafood": 2}, "Quito": {"Ecuadorian": 4}}
ALL_CITIES = list(FD_CITIES)
PROMOTIONS = (
    ("WELCOME20", "20% off your first order", "percent_off", 20, "new customers", ALL_CITIES, "2025-01-01", None),
    ("AMIGO", "Invite a friend: 8 off for both of you", "amount_off", 8, "referred customers", ALL_CITIES,
     "2025-02-01", None),
    ("QUITOGRATIS", "Free delivery on every order in Quito", "free_delivery", None, "all customers", ["Quito"],
     "2025-03-01", "2025-04-30"),
    ("LOYAL10", "10% off every order for returning customers", "percent_off", 10, "returning customers",
     ALL_CITIES, "2025-04-01", "2026-06-30"),
    ("CEVICHE5", "5 off seafood orders for Ceviche Day week", "amount_off", 5, "all customers", ["Lima"],
     "2025-06-28", "2025-07-05"),
    ("LLUVIA15", "15% off on rainy-season evenings", "percent_off", 15, "all customers", ["Bogotá", "Medellín"],
     "2025-10-01", "2025-11-30"),
    ("BLACKFRIDAY25", "25% off for Black Friday weekend", "percent_off", 25, "all customers", ALL_CITIES,
     "2025-11-28", "2025-11-30"),
    ("NAVIDAD", "Free delivery on orders over 40 in December", "free_delivery", None, "all customers", ALL_CITIES,
     "2025-12-15", "2025-12-31"),
    ("LUNCH10", "10% off weekday lunch orders", "percent_off", 10, "all customers", ["Medellín", "Cali"],
     "2026-02-01", "2026-04-30"),
    ("FUTBOL", "Free delivery during the football tournament", "free_delivery", None, "all customers", ALL_CITIES,
     "2026-06-11", "2026-07-19"),
    ("VUELVE15", "15% off to welcome back customers who have not ordered for 60 days", "percent_off", 15,
     "lapsed customers", ALL_CITIES, "2026-09-15", "2026-10-31"),
    ("STUDENT5", "5 off for verified students", "amount_off", 5, "students", ["Bogotá", "Lima", "Quito"],
     "2026-08-01", None),
)
FD_SCHEMA = """
CREATE TABLE restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    cuisine       TEXT NOT NULL,
    city          TEXT NOT NULL,
    price_level   INTEGER NOT NULL CHECK (price_level BETWEEN 1 AND 3),
    joined_on     TEXT NOT NULL
);
CREATE TABLE orders (
    order_id         INTEGER PRIMARY KEY,
    customer_id      INTEGER NOT NULL,
    restaurant_id    INTEGER NOT NULL REFERENCES restaurants (restaurant_id),
    ordered_at       TEXT NOT NULL,
    items            INTEGER NOT NULL,
    subtotal         REAL NOT NULL,
    delivery_fee     REAL NOT NULL,
    discount         REAL NOT NULL,
    total            REAL NOT NULL,
    promo_code       TEXT,
    payment_method   TEXT NOT NULL,
    distance_km      REAL NOT NULL,
    promised_minutes INTEGER NOT NULL,
    delivery_minutes INTEGER,
    status           TEXT NOT NULL CHECK (status IN ('delivered', 'cancelled')),
    rating           INTEGER CHECK (rating BETWEEN 1 AND 5)
);
"""
MEAL_HOURS = np.array([0.3, 0.1, 0.05, 0.03, 0.03, 0.05, 0.2, 0.6, 1.0, 1.0, 1.4, 3.0, 6.0, 5.5, 2.5, 1.2,
                       1.2, 1.8, 3.5, 6.0, 6.5, 4.0, 2.0, 0.8])
FD_END = date(2026, 9, 30)


@dataclass
class FoodCustomer:
    customer_id: int
    city: str
    signup: date
    channel: str
    platform: str
    age_band: str
    opt_in: bool
    propensity: float


def fd_restaurants(rng: Rng) -> list[tuple]:
    rows = []
    for city, count in FD_RESTAURANTS.items():
        cuisines = list(CUISINES)
        weight = np.array([LOCAL_CUISINE[city].get(c, 1.0) for c in cuisines])
        used: set[str] = set()
        while len([r for r in rows if r[3] == city]) < count:
            cuisine = pick(rng, cuisines, 1, weight)[0]
            level, bases = CUISINES[cuisine]
            hood = NEIGHBOURHOODS[city][int(rng.integers(len(NEIGHBOURHOODS[city])))]
            name = f"{bases[int(rng.integers(len(bases)))]} {hood}"
            if name in used:
                continue
            used.add(name)
            if rng.random() < 0.7:       # signed before the launch on 2025-01-01
                joined = date(2024, 10, 1) + timedelta(days=int(rng.integers(0, 92)))
            else:
                joined = date(2025, 1, 1) + timedelta(days=int(rng.integers(0, 546)))
            rows.append((len(rows) + 1, name, cuisine, city, level, joined.isoformat()))
    return rows


def fd_customers(rng: Rng) -> list[FoodCustomer]:
    customers = []
    months = [(2025 + (m // 12), m % 12 + 1) for m in range(21)]
    channels = ["organic", "referral", "paid_social", "search", "partner_promo"]
    for k, (year, month) in enumerate(months):
        campaign = (year, month) >= (2026, 7)
        n = int(rng.poisson((150 + 5.5 * k) * (1.6 if campaign else 1.0)))
        first = date(year, month, 1)
        length = ((first + timedelta(days=32)).replace(day=1) - first).days
        mix = [0.25, 0.14, 0.45, 0.10, 0.06] if campaign else [0.35, 0.20, 0.20, 0.15, 0.10]
        for day, city, channel, platform, age, opt_in in zip(
                np.sort(rng.integers(0, length, n)), pick(rng, ALL_CITIES, n, list(FD_CITIES.values())),
                pick(rng, channels, n, mix), pick(rng, ["android", "ios", "web"], n, [0.58, 0.30, 0.12]),
                pick(rng, ["18-24", "25-34", "35-44", "45-54", "55+"], n, [0.25, 0.38, 0.20, 0.10, 0.07]),
                rng.random(n) < 0.55, strict=True):
            propensity = ({"organic": 1.0, "referral": 1.2, "paid_social": 0.6, "search": 0.95,
                           "partner_promo": 0.75}[channel] * {"android": 1.0, "ios": 1.05, "web": 0.85}[platform]
                          * (1.1 if age == "25-34" else 1.0) * float(rng.lognormal(0, 0.3)))
            customers.append(FoodCustomer(50_001 + len(customers), city, first + timedelta(days=int(day)),
                                          channel, platform, age, bool(opt_in), propensity))
    return customers


def active(promo: tuple, when: date, city: str) -> bool:
    _, _, _, _, _, cities, start, end = promo
    return city in cities and date.fromisoformat(start) <= when <= date.fromisoformat(end or "2099-12-31")


def allowed(code: str, c: FoodCustomer, cuisine: str, t: datetime, subtotal: float, gap: int | None) -> bool:
    """The conditions in a promotion's name: seafood orders, evenings, orders over 40, and so on."""
    return {"CEVICHE5": cuisine in ("Seafood", "Peruvian"), "LLUVIA15": t.hour >= 18, "NAVIDAD": subtotal > 40,
            "LUNCH10": t.weekday() < 5 and 11 <= t.hour < 15, "VUELVE15": gap is not None and gap >= 60,
            "STUDENT5": c.age_band == "18-24"}.get(code, True)


def fd_orders(rng: Rng, customers: list[FoodCustomer], restaurants: list[tuple]) -> list[dict]:
    """Simulate each customer's orders: a first order on sign-up, then repeats while they stay."""
    promos = {p[0]: p for p in PROMOTIONS}
    by_city = defaultdict(list)
    for r in restaurants:
        by_city[r[3]].append(r)
    appeal = rng.lognormal(0, 0.6, len(restaurants) + 1)
    meal = MEAL_HOURS / MEAL_HOURS.sum()
    orders = []
    for c in customers:
        when, first, favourites, previous = c.signup, True, [], None
        while when <= FD_END:
            open_now = [r for r in by_city[c.city] if date.fromisoformat(r[5]) <= when]
            if favourites and rng.random() < 0.4:
                restaurant = favourites[int(rng.integers(len(favourites)))]
            else:
                w = np.array([appeal[r[0]] for r in open_now])
                restaurant = open_now[int(rng.choice(len(open_now), p=w / w.sum()))]
                favourites.append(restaurant)
            hour = int(rng.choice(24, p=meal))
            ordered_at = datetime(when.year, when.month, when.day, hour, int(rng.integers(60)), int(rng.integers(60)))
            distance = float(np.clip(rng.gamma(2.0, 1.6), 0.3, 12.0))
            promised = int(min(60, max(25, 5 * round((24 + 2.4 * distance) / 5))))
            peak = 1.25 if hour in (12, 13, 19, 20) else 1.0
            minutes = rng.lognormal(np.log(13), 0.35) + distance * 3.0 * FD_TRAFFIC[c.city] * peak + rng.normal(0, 4)
            if c.city == "Lima" and when >= date(2026, 7, 1):
                minutes += 2 + rng.exponential(4)       # a courier shortage in Lima from July 2026
            minutes = int(max(8, round(minutes)))
            level = restaurant[4]
            items = int(min(6, 1 + rng.poisson(1.0)))
            subtotal = round(items * rng.uniform(7, 13) * {1: 0.8, 2: 1.0, 3: 1.45}[level], 2)
            fee = round((2.9 if when >= date(2026, 8, 1) else 2.5) + 0.35 * max(0.0, distance - 3), 2)
            code = None
            if first:
                if c.channel == "referral" and rng.random() < 0.6:
                    code = "AMIGO"
                elif rng.random() < 0.7:
                    code = "WELCOME20"
            elif active(promos["LOYAL10"], when, c.city) and rng.random() < 0.6:
                code = "LOYAL10"
            if code is None:
                gap = None if previous is None else (when - previous).days
                usable = [p for p in ("QUITOGRATIS", "CEVICHE5", "LLUVIA15", "BLACKFRIDAY25", "NAVIDAD",
                                      "LUNCH10", "FUTBOL", "VUELVE15", "STUDENT5")
                          if active(promos[p], when, c.city)
                          and allowed(p, c, restaurant[2], ordered_at, subtotal, gap)]
                if usable and rng.random() < 0.45:
                    code = usable[int(rng.integers(len(usable)))]
            kind, value = (promos[code][2], promos[code][3]) if code else ("", 0)
            discount = {"percent_off": round(subtotal * (value or 0) / 100, 2), "amount_off": min(value or 0, subtotal),
                        "free_delivery": fee, "": 0.0}[kind]
            cancelled = rng.random() < 0.035
            late = max(0, minutes - promised)
            rating = None
            if not cancelled and rng.random() < 0.55:
                rating = int(np.clip(round(4.6 - 0.09 * late + rng.normal(0, 0.6)), 1, 5))
            orders.append({
                "customer": c, "restaurant": restaurant, "ordered_at": ordered_at, "items": items,
                "subtotal": subtotal, "fee": fee, "discount": round(float(discount), 2),
                "total": round(subtotal + fee - float(discount), 2), "code": code,
                "payment": pick(rng, ["card", "cash", "wallet"], 1,
                                [0.47, 0.35, 0.18] if c.city == "Lima" else [0.54, 0.26, 0.20])[0],
                "distance": round(distance, 1), "promised": promised,
                "minutes": None if cancelled else minutes, "status": "cancelled" if cancelled else "delivered",
                "rating": rating, "late": not cancelled and minutes > promised})
            loyal = active(promos["LOYAL10"], when, c.city)
            stay = (0.70 + 0.12 * np.log(c.propensity) - (0.22 if orders[-1]["late"] else 0.0)
                    + (0.10 if loyal else 0.0) - (0.08 if rating is not None and rating <= 2 else 0.0))
            if rng.random() > min(0.93, max(0.05, stay)):
                break
            first, previous = False, when
            when += timedelta(days=int(1 + rng.exponential(13 / c.propensity * (0.8 if loyal else 1.0))))
    orders.sort(key=lambda o: (o["ordered_at"], o["customer"].customer_id))
    for k, o in enumerate(orders):
        o["order_id"] = 700_001 + k
    return orders


def fd_story_checks(orders: list[dict]) -> None:
    """The P3 question must have an answer: repeat orders fell in 2026-Q3, for more than one reason."""
    def quarter(t: datetime) -> str:
        return f"{t.year}-Q{(t.month - 1) // 3 + 1}"

    seen: set[int] = set()
    repeat, total = Counter(), Counter()
    first_order: dict[int, dict] = {}
    for o in orders:
        cid = o["customer"].customer_id
        q = quarter(o["ordered_at"])
        total[q] += 1
        repeat[q] += cid in seen
        seen.add(cid)
        first_order.setdefault(cid, o)
    assert repeat["2026-Q3"] < 0.93 * repeat["2026-Q2"], (repeat["2026-Q2"], repeat["2026-Q3"])
    assert total["2026-Q3"] > total["2026-Q2"], (total["2026-Q2"], total["2026-Q3"])
    late = defaultdict(list)
    for o in orders:
        if o["status"] == "delivered":
            late[o["customer"].city, quarter(o["ordered_at"])].append(o["late"])
    change = {city: float(np.mean(late[city, "2026-Q3"]) - np.mean(late[city, "2026-Q2"])) for city in FD_CITIES}
    assert change["Lima"] > 0.12 and max(abs(v) for c, v in change.items() if c != "Lima") < 0.05, change
    second: dict[int, datetime] = {}
    for o in orders:
        cid = o["customer"].customer_id
        if o is not first_order[cid] and cid not in second:
            second[cid] = o["ordered_at"]
    window = [o for o in first_order.values() if o["ordered_at"].date() <= FD_END - timedelta(days=30)]

    def rate(group: list[dict]) -> float:
        cids = [o["customer"].customer_id for o in group]
        return float(np.mean([cid in second and (second[cid] - first_order[cid]["ordered_at"]).days <= 30
                              for cid in cids]))

    on_time, late_first = rate([o for o in window if not o["late"]]), rate([o for o in window if o["late"]])
    assert on_time - late_first > 0.08, (on_time, late_first)
    by_channel = {ch: rate([o for o in window if o["customer"].channel == ch]) for ch in ("organic", "paid_social")}
    assert by_channel["organic"] - by_channel["paid_social"] > 0.05, by_channel


MESSY_CITY = {
    "Bogotá": ("Bogota", "bogota", "BOGOTÁ", " Bogotá", "Bogotá ", "bogotá"),
    "Medellín": ("Medellin", "medellin", "MEDELLIN", "Medellín "),
    "Cali": ("cali", "CALI", "Cali "),
    "Lima": ("lima", "LIMA", " Lima"),
    "Quito": ("quito", "QUITO", "Quito "),
}
MESSY_PAYMENT = {"card": ("Card", "CARD", "credit card", "debit card"), "cash": ("Cash", "CASH", "cash "),
                 "wallet": ("Wallet", "e-wallet", "digital wallet")}
MESSY_STATUS = {"delivered": ("Delivered", "DELIVERED"), "cancelled": ("canceled", "Cancelled", "CANCELLED")}


def messy(rng: Rng, value: str, variants: Sequence[str], rate: float) -> str:
    return variants[int(rng.integers(len(variants)))] if rng.random() < rate else value


def fd_messy_rows(rng: Rng, orders: list[dict]) -> list[list]:
    """Q1 2026 orders as exported by the old order system, with the kinds of mess real exports have."""
    rows = []
    for o in orders:
        t = o["ordered_at"]
        if not date(2026, 1, 1) <= t.date() <= date(2026, 3, 31):
            continue
        if rng.random() < 0.15:
            when = t.strftime("%Y/%m/%d %H:%M")
        else:
            when = stamp(t)
        if rng.random() < 0.0015:
            when = when.replace("2026", "2036", 1)
        money = [f2(o["subtotal"]), f2(o["fee"]), f2(o["total"])]
        if rng.random() < 0.10:
            money = [m.replace(".", ",") for m in money]
        minutes = "" if o["minutes"] is None else str(o["minutes"])
        if minutes:
            u = rng.random()
            if u < 0.08:
                minutes = f"{minutes} min"
            elif u < 0.09:
                minutes = f"-{minutes}"
            elif u < 0.10:
                minutes = "999"
        distance = o["distance"]
        u = rng.random()
        if u < 0.005:
            distance = -distance
        elif u < 0.008:
            distance = round(float(rng.uniform(150, 400)), 1)
        rating = "" if o["rating"] is None else str(o["rating"])
        if rng.random() < 0.015:
            rating = str(int(rng.choice([0, 6, 10])))
        city = o["restaurant"][3]
        cuisine = o["restaurant"][2]
        if rng.random() < 0.08:
            cuisine = cuisine.lower() if rng.random() < 0.5 else cuisine.upper()
        payment = "" if rng.random() < 0.01 else messy(rng, o["payment"], MESSY_PAYMENT[o["payment"]], 0.25)
        rows.append([o["order_id"], when, o["customer"].customer_id, o["restaurant"][1], cuisine,
                     messy(rng, city, MESSY_CITY[city], 0.25), o["items"], *money, payment,
                     messy(rng, o["status"], MESSY_STATUS[o["status"]], 0.2), f1(distance), minutes, rating])
    for k in sorted(rng.choice(len(rows), 60, replace=False), reverse=True):
        rows.insert(int(k) + int(rng.integers(1, 30)), list(rows[k]))
    return rows


def make_food_delivery(rng: Rng) -> Files:
    """P3 (and the M12 project): a fictional food-delivery company in five cities, 2025-01-01 to 2026-09-30.

    food_delivery.db holds restaurants and every order; food_delivery_customers.csv holds the customers (no
    names: the company pseudonymises them); food_delivery_promotions.json is what the mock promotions API
    serves; food_delivery_messy.csv is a Q1 2026 export from the old order system for the M12 cleaning
    challenge. Planted for P3 ("why did repeat orders fall last quarter?"): in 2026-Q3, total orders grow but
    orders from returning customers fall, because (1) the LOYAL10 promotion for returning customers ended on
    2026-06-30, (2) a courier shortage in Lima from July makes deliveries late, and late first orders lead
    to fewer second orders, and (3) a paid-social campaign brings many new customers who reorder less.
    Censoring trap: customers who signed up in the last 30 days have not had a full 30-day window.
    The messy export has exact duplicate rows, city/payment/status label variants, decimal commas, mixed
    date formats, a few 2036 typos, minutes as text ("35 min"), negative or 999 minutes, negative or huge
    distances and ratings outside 1-5.
    """
    restaurants = fd_restaurants(rng)
    customers = fd_customers(rng)
    orders = fd_orders(rng, customers, restaurants)
    fd_story_checks(orders)
    order_rows = [(o["order_id"], o["customer"].customer_id, o["restaurant"][0], stamp(o["ordered_at"]), o["items"],
                   o["subtotal"], o["fee"], o["discount"], o["total"], o["code"], o["payment"], o["distance"],
                   o["promised"], o["minutes"], o["status"], o["rating"]) for o in orders]
    customer_rows = [(c.customer_id, c.city, c.signup.isoformat(), c.channel, c.platform, c.age_band,
                      yes_no(c.opt_in)) for c in customers]
    promotions = [{"promo_code": code, "name": name, "kind": kind, "value": value, "audience": audience,
                   "cities": cities, "start_date": start, "end_date": end}
                  for code, name, kind, value, audience, cities, start, end in PROMOTIONS]
    return {
        "food_delivery.db": sqlite_bytes(FD_SCHEMA, {
            "restaurants": (("restaurant_id", "name", "cuisine", "city", "price_level", "joined_on"), restaurants),
            "orders": (("order_id", "customer_id", "restaurant_id", "ordered_at", "items", "subtotal", "delivery_fee",
                        "discount", "total", "promo_code", "payment_method", "distance_km", "promised_minutes",
                        "delivery_minutes", "status", "rating"), order_rows)}),
        "food_delivery_customers.csv": csv_bytes(("customer_id", "city", "signup_date", "acquisition_channel",
                                                  "platform", "age_band", "marketing_opt_in"), customer_rows),
        "food_delivery_promotions.json": json_bytes({"promotions": promotions}),
        "food_delivery_messy.csv": csv_bytes(
            ("order_id", "order_time", "customer_id", "restaurant", "cuisine", "city", "items", "subtotal",
             "delivery_fee", "total", "payment", "status", "distance_km", "delivery_minutes", "rating"),
            fd_messy_rows(rng, orders)),
    }


# ----------------------------------------------------------------------------- students
PROGRAMMES = ("Computer Science", "Data Science", "Engineering", "Business", "Biology", "Design")


def make_student_performance(rng: Rng) -> Files:
    """M13-L04 (and M13, M14 examples): 1,000 students at a fictional university, one row per student.

    Planted: final_exam depends mostly on previous_grade, then on study hours (diminishing returns),
    attendance, sleep (best near 7.5 hours), paid work (negative) and tutoring (+5 points). Tutoring was
    offered mostly to students with low previous grades, so tutored students score LOWER overall but HIGHER
    within every previous-grade band (below 55, 55-70, 70 and above): Simpson's paradox. Missing values:
    sleep_hours (5%), commute_minutes (3%). Three study_hours values are data-entry errors (over 100 a week).
    """
    n = 1000
    programme = pick(rng, PROGRAMMES, n, [0.25, 0.15, 0.20, 0.20, 0.10, 0.10])
    year = rng.choice([1, 2, 3], n, p=[0.38, 0.33, 0.29])
    mature = rng.random(n) < 0.06
    age = 17 + year + rng.poisson(0.6, n) + mature * rng.integers(4, 12, n)
    previous = np.clip(rng.normal(66, 12, n), 30, 98)
    study = np.clip(rng.gamma(3.0, 4.0, n) + 0.08 * (previous - 66), 0, 45)
    attendance = np.clip(100 * rng.beta(8, 1.8, n) + 0.15 * (previous - 66), 25, 100)
    sleep = np.clip(rng.normal(7.1, 1.0, n), 4, 10)
    work = np.where(rng.random(n) < 0.55, 0, rng.integers(4, 31, n))
    commute = np.clip(np.round(rng.gamma(2.0, 15.0, n)), 5, 120)
    tutoring = rng.random(n) < np.select([previous < 55, previous < 70], [0.7, 0.25], 0.08)   # offered by grade
    internet = rng.random(n) < 0.92
    extra = rng.random(n) < 0.42
    final = (-5 + 0.8 * previous + 3.2 * np.log1p(study) + 0.15 * (attendance - 80) - 1.8 * (sleep - 7.5) ** 2
             - 0.25 * work + 5 * tutoring - 0.03 * commute + 2 * internet + rng.normal(0, 6, n))
    final = np.clip(np.round(final), 0, 100).astype(int)
    overall = final[tutoring].mean() - final[~tutoring].mean()
    bands = [(previous < 55), (previous >= 55) & (previous < 70), (previous >= 70)]
    within = [final[b & tutoring].mean() - final[b & ~tutoring].mean() for b in bands]
    assert overall < -2 and min(within) > 2, (overall, within)
    study_out = np.round(study, 1)
    study_out[rng.choice(n, 3, replace=False)] = [120.0, 150.0, 105.0]
    sleep_missing, commute_missing = rng.random(n) < 0.05, rng.random(n) < 0.03
    rows = [(f"S{k + 1:04d}", programme[k], int(year[k]), int(age[k]), f1(previous[k]), f1(study_out[k]),
             f1(attendance[k]), None if sleep_missing[k] else f1(sleep[k]), int(work[k]),
             None if commute_missing[k] else int(commute[k]), yes_no(tutoring[k]), yes_no(internet[k]),
             yes_no(extra[k]), int(final[k]), yes_no(final[k] >= 50)) for k in range(n)]
    header = ("student_id", "programme", "year", "age", "previous_grade", "study_hours", "attendance_pct",
              "sleep_hours", "work_hours", "commute_minutes", "tutoring", "internet_at_home", "extracurricular",
              "final_exam", "passed")
    return {"student_performance.csv": csv_bytes(header, rows)}


# ----------------------------------------------------------------------------- housing
DISTRICTS = {  # name: (log-price offset, typical distance to the centre in km)
    "Old Town": (0.30, 1.2), "Riverside": (0.22, 2.5), "Harbour": (0.18, 3.2), "University": (0.05, 3.8),
    "Hillcrest": (0.25, 6.0), "Greenfield": (-0.05, 8.5), "Lakeside": (0.10, 9.5), "Industrial Park": (-0.25, 7.0),
}


def make_housing(rng: Rng) -> Files:
    """M16 project: 1,500 home sales in a fictional city; the target is price.

    Planted: log(price) rises with log(area) and falls with distance to the centre; districts add premiums;
    a station within about 1 km adds up to 8%; gardens, parking, better energy ratings and condition add
    smaller premiums; new builds and historic Old Town homes cost more. bedrooms and bathrooms are strongly
    correlated with area (Ridge helps), and the station effect is non-linear (k-NN can find it). No missing
    values, because M16 comes before imputation (M17).
    """
    n = 1500
    names = list(DISTRICTS)
    district = pick(rng, names, n, [0.10, 0.12, 0.10, 0.12, 0.13, 0.17, 0.12, 0.14])
    kind = pick(rng, ["apartment", "terraced house", "detached house"], n, [0.55, 0.25, 0.20])
    base_area = np.array([{"apartment": 70, "terraced house": 105, "detached house": 160}[k] for k in kind])
    area = np.clip(np.round(base_area * rng.lognormal(0, 0.25, n)), 25, 450)
    bedrooms = np.clip(np.round(area / 32 + rng.normal(0, 0.6, n)), 1, 7).astype(int)
    bathrooms = np.clip(np.round(area / 75 + rng.normal(0.3, 0.45, n)), 1, 4).astype(int)
    old_town = np.array([d == "Old Town" for d in district])
    year = np.where(old_town & (rng.random(n) < 0.6), rng.integers(1880, 1960, n), rng.integers(1955, 2026, n))
    centre = np.array([DISTRICTS[d][1] for d in district]) * rng.lognormal(0, 0.25, n)
    station = rng.lognormal(np.log(1.4), 0.7, n).clip(0.1, 8)
    garden = rng.random(n) < np.array([{"apartment": 0.08, "terraced house": 0.7, "detached house": 0.92}[k]
                                       for k in kind])
    parking = rng.random(n) < np.where(old_town, 0.2, 0.6)
    energy_index = np.clip(np.round(3.2 - (year - 1990) / 14 + rng.normal(0, 0.9, n)), 0, 6).astype(int)
    condition = rng.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.15, 0.4, 0.28, 0.12])
    age_effect = np.where(year >= 2015, 0.06, np.where(year < 1930, np.where(old_town, 0.05, -0.03),
                                                       np.where((year >= 1960) & (year < 1990), -0.04, 0.0)))
    log_price = (12.0 + np.array([DISTRICTS[d][0] for d in district]) + 0.9 * np.log(area / 80)
                 + 0.04 * bathrooms + np.array([{"apartment": 0.0, "terraced house": 0.03,
                                                  "detached house": 0.08}[k] for k in kind])
                 - 0.025 * centre + 0.08 * np.exp(-station / 0.8) + 0.05 * garden + 0.04 * parking
                 + 0.03 * (3 - energy_index) + 0.04 * (condition - 3) + age_effect + rng.normal(0, 0.10, n))
    price = (np.round(np.exp(log_price) / 100) * 100).astype(int)
    rows = [(district[k], kind[k], int(area[k]), int(bedrooms[k]), int(bathrooms[k]), int(year[k]), f1(centre[k]),
             f1(station[k]), yes_no(garden[k]), yes_no(parking[k]), "ABCDEFG"[energy_index[k]], int(condition[k]),
             int(price[k])) for k in range(n)]
    header = ("district", "property_type", "area_m2", "bedrooms", "bathrooms", "year_built", "distance_centre_km",
              "distance_station_km", "garden", "parking", "energy_rating", "condition", "price")
    return {"housing_small.csv": csv_bytes(header, rows)}


# ----------------------------------------------------------------------------- telco churn
AGE_BANDS = ("18-24", "25-34", "35-44", "45-54", "55-64", "65+")


def telco_rows(rng: Rng, n: int, first_id: int, drift: bool, shift: float | None) -> tuple[list[tuple], float]:
    """n customers; drift=True makes the later batch (data drift and concept drift: see make_telco_churn)."""
    region = pick(rng, ["North", "South", "East", "West", "Central"], n, [0.22, 0.20, 0.22, 0.20, 0.16])
    age = pick(rng, AGE_BANDS, n, [0.15, 0.27, 0.22, 0.16, 0.12, 0.08] if drift else [0.12, 0.24, 0.22, 0.18,
                                                                                         0.14, 0.10])
    senior = np.array([a == "65+" for a in age])
    tenure = np.where(rng.random(n) < 0.08, 72, np.minimum(72, np.floor(rng.exponential(24, n)))).astype(int)
    p_monthly = np.clip(0.78 - 0.008 * tenure, 0.2, 0.8)
    u = rng.random(n)
    contract = np.where(u < p_monthly, "month-to-month",
                        np.where(u < p_monthly + (1 - p_monthly) * 0.5, "one-year", "two-year"))
    internet = np.array(pick(rng, ["fibre", "dsl", "none"], n, [0.55, 0.30, 0.15] if drift else [0.45, 0.35, 0.20]))
    internet[senior & (rng.random(n) < 0.3)] = "dsl"
    has_net = internet != "none"
    streaming = has_net & (rng.random(n) < np.where(internet == "fibre", 0.6, 0.35))
    support = has_net & (rng.random(n) < 0.35)
    lines = np.clip(1 + rng.poisson(0.9, n), 1, 5)
    methods = ["card", "bank-transfer", "e-wallet", "cash"] + (["instant-pay"] if drift else [])
    mix = [0.34, 0.25, 0.19, 0.14, 0.08] if drift else [0.38, 0.27, 0.20, 0.15]
    payment = np.array(pick(rng, methods, n, mix))
    payment[senior & (rng.random(n) < 0.25)] = "cash"
    paperless = rng.random(n) < np.where(senior, 0.35, 0.65)
    charges = (12 + 8 * lines + np.select([internet == "fibre", internet == "dsl"], [45, 28], 0) + 9 * streaming
               + 6 * support + rng.normal(0, 3, n)) * (1.07 if drift else 1.0)
    charges = np.round(np.clip(charges, 15, 160), 2)
    total = np.round(charges * tenure * rng.uniform(0.95, 1.02, n), 2)
    usage = np.select([internet == "fibre", internet == "dsl"],
                      [rng.lognormal(3.8, 0.5, n), rng.lognormal(3.2, 0.5, n)], rng.uniform(1, 15, n))
    usage = np.round(usage * (1.15 if drift else 1.0), 1)
    east_outage = drift & (np.array(region) == "East")
    calls = rng.poisson(0.8 + 1.2 * ((internet == "fibre") & ~support) + 0.8 * east_outage)
    age_young = np.array([a == "18-24" for a in age])
    late = rng.poisson(0.3 + 0.6 * (payment == "cash") + 0.3 * age_young)
    satisfaction = np.clip(np.round(3.6 - 0.35 * calls - 0.004 * (charges - 70) + rng.normal(0, 0.9, n)), 1, 5)
    responded = rng.random(n) < np.where(satisfaction >= 4, 0.85, 0.68)
    central = np.array([r == "Central" for r in region])
    if drift:   # a competitor buys out contracts, the outage and the new payment method raise churn
        terms = {"month-to-month": 0.9, "one-year": 0.45, "two-year": 0.1}
    else:
        terms = {"month-to-month": 1.6, "one-year": 0.4, "two-year": 0.0}
    logit = (np.array([terms[c] for c in contract]) - (0.015 if drift else 0.035) * tenure
             + (0.03 if drift else 0.018) * (charges - 65)
             + 0.32 * calls + 0.25 * late - 0.45 * (satisfaction - 3) + 0.5 * ((internet == "fibre") & ~support)
             + 0.6 * central + central * rng.normal(0, 1.8, n) + 0.25 * age_young + 0.2 * senior
             + 0.9 * east_outage + 0.6 * (payment == "instant-pay") + rng.normal(0, 0.4, n))
    if shift is None:
        shift = shift_to_rate(logit, 0.205)
    churn = rng.random(n) < sigmoid(logit + shift)
    rows = [(f"C-{first_id + k}", region[k], age[k], int(tenure[k]), str(contract[k]), str(payment[k]),
             yes_no(paperless[k]), str(internet[k]), yes_no(streaming[k]), yes_no(support[k]), int(lines[k]),
             f2(charges[k]), None if tenure[k] == 0 else f2(total[k]), f1(usage[k]), int(calls[k]), int(late[k]),
             int(satisfaction[k]) if responded[k] else None, yes_no(churn[k])) for k in range(n)]
    return rows, shift


def make_telco_churn(rng: Rng) -> Files:
    """P4 (and M17, M19, M24): telecom customers on 2026-06-30; churn says who left in July 2026.

    telco_churn_current.csv is the batch scored three months later (P6 and M25-L06 drift): prices rose 7%,
    fibre is more common, a new payment method (instant-pay) appears, data usage is up 15%, an outage raised
    support calls in East, and the age mix is younger (data drift). Churn also follows new rules (concept
    drift): it reacts more to price and less to tenure and contract (a competitor buys out contracts), and
    rises in East and among instant-pay users, so a model trained on telco_churn.csv scores worse on it.
    Planted: about 20% churn, driven by month-to-month contracts, short tenure, high charges, support calls,
    late payments, low satisfaction, and fibre without tech support; churn in Central is higher and noisier
    (a competitor the data does not show), so it is the weakest segment in error analysis. satisfaction is
    missing for survey non-responders (less often answered by unhappy customers); total_charges is empty for
    customers in their first month (tenure 0).
    """
    reference, shift = telco_rows(rng, 7000, 100_001, drift=False, shift=None)
    current, _ = telco_rows(rng, 2000, 200_001, drift=True, shift=shift)
    header = ("customer_id", "region", "age_band", "tenure_months", "contract", "payment_method", "paperless_billing",
              "internet_service", "streaming_tv", "tech_support", "mobile_lines", "monthly_charges", "total_charges",
              "data_usage_gb", "support_calls_90d", "late_payments_12m", "satisfaction", "churn")
    rate = np.mean([r[-1] == "yes" for r in reference])
    later = np.mean([r[-1] == "yes" for r in current])
    assert 0.18 < rate < 0.23 and later > rate + 0.04, (rate, later)
    return {"telco_churn.csv": csv_bytes(header, reference), "telco_churn_current.csv": csv_bytes(header, current)}


# ----------------------------------------------------------------------------- card fraud
FRAUD_CATEGORIES = ("grocery", "restaurants", "fuel", "transport", "pharmacy", "utilities", "fashion",
                    "electronics", "travel", "online_gaming", "gift_cards")
CATEGORY_AMOUNT = (1.0, 0.7, 1.1, 0.3, 0.6, 1.8, 1.6, 3.0, 5.0, 0.5, 1.2)
LEGIT_MIX = (0.22, 0.16, 0.10, 0.13, 0.08, 0.07, 0.09, 0.06, 0.03, 0.03, 0.03)
FRAUD_MIX = (0.06, 0.05, 0.04, 0.02, 0.02, 0.0, 0.14, 0.25, 0.10, 0.14, 0.18)
ONLINE_ONLY = {"utilities", "online_gaming"}
DAY_HOURS = np.array([1, 0.6, 0.4, 0.3, 0.3, 0.5, 1.5, 3, 4, 4.5, 5, 5.5, 6, 5.5, 5, 5, 5.5, 6, 6, 5.5, 4.5,
                      3.5, 2.5, 1.5])


def make_transactions_fraud(rng: Rng) -> Files:
    """M17-L07 (and M16-L07, M25-L07): 15,000 card payments in April 2026; is_fraud marks the fraudulent ones.

    Planted: about 2.5% fraud, and no single column gives it away. Most fraud comes in bursts from about 55
    compromised cards: several payments within hours (so txn_last_24h is high), sometimes starting with
    small "card testing" amounts, mostly online, often abroad, at night, from a new device or in risky
    categories. About 70 single frauds are harder to spot. Many legitimate payments look risky too:
    travellers pay abroad, people buy from foreign websites, buy electronics and gift cards, pay several
    times a day and change phones. card_id groups payments by card: use GroupKFold, and never use card_id
    itself as a feature. is_foreign means the merchant is abroad; distance_from_home_km is measured from
    where the payment was made (the shop, or the device for online payments).
    """
    n_total, n_cards = 15_000, 2500
    start = datetime(2026, 4, 1)
    activity = rng.lognormal(0, 0.9, n_cards)
    spend = rng.lognormal(np.log(45), 0.5, n_cards)
    card_age = rng.integers(20, 3000, n_cards)
    trip = rng.random(n_cards) < 0.10
    trip_start, trip_days = rng.integers(0, 27, n_cards), rng.integers(3, 11, n_cards)
    rows = []   # card, time, category, channel, amount, foreign, distance, new_device, fraud

    def add(card: int, t: datetime, category: int, channel: str, amount: float, foreign: bool,
            distance: float, new_device: bool, fraud: bool) -> None:
        rows.append((card, t, category, channel, round(max(1.0, amount), 2), foreign, distance, new_device, fraud))

    for card in rng.choice(n_cards, 55, replace=False, p=activity / activity.sum()):
        t = start + timedelta(minutes=int(rng.integers(0, 29 * 24 * 60)))
        if rng.random() < 0.4:
            t = t.replace(hour=int(rng.integers(0, 5)))
        online, foreign = rng.random() < 0.7, rng.random() < 0.4
        for k in range(int(rng.integers(3, 10))):
            testing = k < 2 and rng.random() < 0.4          # small "card testing" payments come first
            amount = rng.uniform(1, 5) if testing else spend[card] * rng.lognormal(np.log(2.3), 0.7)
            add(card, t, int(rng.choice(11, p=FRAUD_MIX)), "online" if online else "in_store", amount, foreign,
                rng.uniform(800, 9000) if foreign else rng.lognormal(np.log(20), 1.2),
                online and rng.random() < 0.55, True)
            t += timedelta(minutes=int(1 + rng.exponential(40)))
    for card in rng.choice(n_cards, 70, replace=False):
        t = start + timedelta(minutes=int(rng.integers(0, 30 * 24 * 60)))
        if rng.random() < 0.3:
            t = t.replace(hour=int(rng.integers(0, 6)))
        foreign = rng.random() < 0.25
        category = int(rng.choice(11, p=FRAUD_MIX if rng.random() < 0.6 else LEGIT_MIX))
        online = rng.random() < 0.85
        add(card, t, category, "online" if online else "in_store", spend[card] * rng.lognormal(np.log(1.6), 0.6),
            foreign, rng.uniform(800, 9000) if foreign else rng.lognormal(np.log(12), 1.1),
            online and rng.random() < 0.35, True)

    n_legit = n_total - len(rows)
    cards = np.sort(rng.choice(n_cards, n_legit, p=activity / activity.sum()))
    days = rng.integers(0, 30, n_legit)
    hours = rng.choice(24, n_legit, p=DAY_HOURS / DAY_HOURS.sum())
    same_day = rng.random(n_legit) < 0.35        # people often pay several times on the same day
    for k in range(1, n_legit):
        if same_day[k] and cards[k] == cards[k - 1]:
            days[k], hours[k] = days[k - 1], min(23, hours[k - 1] + int(rng.integers(0, 4)))
    categories = rng.choice(11, n_legit, p=LEGIT_MIX)
    for card, day, hour, category in zip(cards, days, hours, categories, strict=True):
        t = start + timedelta(days=int(day), hours=int(hour), minutes=int(rng.integers(60)),
                              seconds=int(rng.integers(60)))
        if FRAUD_CATEGORIES[category] in ONLINE_ONLY:
            channel = "online"
        else:
            channel = pick(rng, ["in_store", "contactless", "online"], 1, [0.45, 0.30, 0.25])[0]
        abroad = trip[card] and trip_start[card] <= day < trip_start[card] + trip_days[card] and channel != "online"
        if abroad:
            distance = rng.uniform(800, 9000)
        elif channel == "online":
            distance = rng.lognormal(np.log(8), 1.4)
        else:
            distance = rng.lognormal(np.log(4), 1.0)
        add(int(card), t, int(category), channel, spend[card] * CATEGORY_AMOUNT[category] * rng.lognormal(0, 0.6),
            abroad or (channel == "online" and rng.random() < 0.06), distance,
            channel == "online" and rng.random() < 0.06, False)
    rows.sort(key=lambda r: (r[1], r[0]))
    recent: dict[int, list[datetime]] = defaultdict(list)
    out = []
    for k, (card, t, category, channel, amount, foreign, distance, new_device, fraud) in enumerate(rows):
        times = [s for s in recent[card] if t - s <= timedelta(hours=24)]
        recent[card] = [*times, t]
        out.append((f"T{k + 1:07d}", stamp(t), f"K{card + 1:05d}", f2(amount), FRAUD_CATEGORIES[category], channel,
                    int(foreign), f1(distance), int(card_age[card] + (t - start).days), len(times),
                    f2(spend[card] * rng.lognormal(0.1, 0.1)), int(new_device), int(fraud)))
    rate = np.mean([r[-1] for r in out])
    assert 0.02 < rate < 0.035, rate
    header = ("transaction_id", "timestamp", "card_id", "amount", "merchant_category", "channel", "is_foreign",
              "distance_from_home_km", "card_age_days", "txn_last_24h", "avg_amount_30d", "new_device", "is_fraud")
    return {"transactions_fraud.csv": csv_bytes(header, out)}


# ----------------------------------------------------------------------------- SMS spam
HAM = (  # personal messages: some use "spam" words (free, win, prize, urgent, money, claim) innocently
    "Are you free on {day}?", "I'm running late, see you at {time}", "Can you pick up some {food} on your way home?",
    "Ok see you at {place}", "Did you finish the assignment for {day}?", "Call me when you land",
    "Happy birthday! Have a great day 🎉", "We won the match!! {num}-{small_num}",
    "Sorry, missed your call. In a meeting until {time}", "Dinner is at {time}", "The bus is {num} min late again",
    "Can we move our meeting to {day} at {time}?", "Thanks for lunch today, it was great",
    "Don't forget to bring the {item}", "I left my {item} at {place}", "Good luck with your exam tomorrow!",
    "Are you coming to {place} tonight?", "Let me know when you get home",
    "Lecture cancelled today, the professor is sick", "Free tonight? Want to watch the match at {place}?",
    "Can you send me the notes from {day}'s class?", "Doctor's appointment moved to {time}",
    "I'll be there in {num} minutes", "Where are you? We're at {place}", "Please call me back, it's urgent",
    "Did you get the money I sent?", "Congrats on the new job!! So proud of you", "lol that's hilarious 😂",
    "Can't talk now, text me", "Taking the {time} train, will be home soon", "Who won the quiz last night?",
    "The wifi password is on the fridge", "Please buy {food} and {food2}", "Meeting room changed to {place}",
    "Table for {small_num} is booked for {time}", "See you tomorrow at {time}", "Can I borrow your bike on {day}?",
    "{name2} is coming too, is that ok?", "Did you win anything at the raffle?",
    "Text me your address and I'll send the invitation", "Prize-giving at school starts at {time}",
    "Are you still at {place}?", "Got it, thanks", "Running {num} min late, sorry!!", "Love you, see you soon",
    "Can you call me after {time}?", "I'm at {place}, where are you?", "Did you see the game last night?",
    "My train is delayed, I'll be {num} minutes late", "Can I come over on {day}?",
    "What time does {place} close?", "I made {food} for dinner, come by if you want", "Are we still on for {day}?",
    "Just woke up, give me {num} min", "Exam went ok I think", "Thanks for the help with the project!",
    "Got your message, will reply later", "Can you lend me {small_amount} until {day}?",
    "I owe you {small_amount} for the tickets", "Grandma is visiting on {day}", "Have you finished the report?",
    "Who's driving on {day}?", "I'll send you the photos tonight", "Lost my {item} again 🙈", "On my way!",
    "Send me the address pls", "Let's meet at {place} at {time}", "Is the library open on {day}?",
    "Your turn to cook tonight 😄", "Football practice is cancelled", "Free on {day} after {time}?",
    "We need {small_num} more people for the team", "I got the job!!!", "The free trial ended so I cancelled it",
    "Call your grandmother, it's her birthday", "Urgent: can you call me? I'm locked out of the flat",
    "The prize for best project went to our group!!", "Don't forget your passport tomorrow",
    "There's free food at {place} after the talk", "You win, I'll pay for the coffee next time 😂",
    "Can you claim the seats near the window? I'm {num} min away", "Is the offer for the room still open?",
    "Mum sent money for the books, I'll transfer your half", "Check your email, I sent the form",
)
HAM_OPENERS = ("", "", "", "", "", "Hey, ", "Hi {name}, ", "{name}, ", "Ok so ", "Btw ", "Hiya! ", "Morning! ",
               "Sorry, ", "Hey {name}! ")
HAM_CLOSERS = ("", "", "", "", "", " 😊", " 👍", " x", " xx", " lol", " haha", " Thanks!", " ok?", " See you!", " 🙏")
SPAM = (
    "WINNER!! You have won a {amount} prize. Call {phone} to claim now!",
    "Congratulations! You have been selected for a free {gift}. Reply YES to claim",
    "URGENT: your bank account has been suspended. Verify now at {url}",
    "Your parcel is waiting. Pay the {fee} delivery fee here: {url}",
    "Hi {name}, your parcel could not be delivered. Update your address: {url}",
    "Get a loan of {amount} today, no credit check! Apply at {url}",
    "You have been chosen for a work-from-home job paying {amount} a week. Text JOB to {short}",
    "FREE entry to win a new phone! Text WIN to {short} now", "Claim your {amount} bonus now! Offer ends tonight {url}",
    "Your account will be closed today. Confirm your details at {url}",
    "Double your money in 7 days with our crypto plan 💰 {url}",
    "Last chance! {pct}% off designer watches, today only: {url}",
    "You have an unpaid toll. Pay now to avoid a fine: {url}",
    "Dear customer, your SIM will be blocked. Call {phone} immediately",
    "You've won a {gift}! To claim it, pay the shipping cost at {url}",
    "Tax refund of {amount} pending. Submit your bank details: {url}",
    "Hi, it's me, I lost my phone. This is my new number. Can you send {small_amount} for a taxi?",
    "Final notice: your subscription renewal of {fee} failed. Update payment: {url}",
    "Txt STOP to {short} to stop your free daily horoscope. {fee}/msg",
    "Earn {amount} per day liking videos online. Message {phone}",
    "Your package from customs needs a payment of {fee}. Pay at {url}",
    "You are eligible for a government grant of {amount}. Apply: {url}", "New friends near you want to chat: {url}",
    "Your bank card has been locked. Call {phone} to unlock it", "Act now! Your {gift} is reserved for 24 hours: {url}",
    "Hi {name}, I'm a recruiter. We have a part-time job for you, {amount} a week. Message me on {phone}",
    "Hey, is this {name}? I found your number in my contacts, are you free to chat?",
    "Your number won {amount} in our monthly draw! Text CLAIM to {short}",
    "Congratulations {name}! Answer 3 questions about your shopping and win a {gift}: {url}",
    "Mum, I dropped my phone in water. Message me on my new number {phone}",
)
SPAM_CLOSERS = ("", "", "", "", " Reply STOP to opt out", " T&Cs apply", " 18+ only", " Don't miss out!")
SERVICE = (  # wanted and unwanted versions read the same (smishing copies real notices): (template, P(ham))
    ("Your parcel {code} is out for delivery today. Track it here: {link}", 0.5),
    ("Your verification code is {code}. Do not share it with anyone.", 0.9),
    ("Reminder: your appointment is on {day} at {time}. Reply C to cancel", 0.8),
    ("Your monthly statement is ready. Log in to view it: {link}", 0.6),
    ("{shop}: {pct}% off everything this weekend! Show this message in store", 0.4),
    ("Your {shop} order has shipped. Track it: {link}", 0.6),
    ("You have won the {prize} in the {place} raffle! Collect it at the front desk", 0.5),
    ("We tried to deliver your parcel today. Book a new delivery: {link}", 0.4),
    ("Your mobile bill of {fee} is due on {day}. Pay in the app or at {link}", 0.6),
)
SMS_SLOTS = {
    "day": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "tomorrow", "tonight"),
    "time": ("7", "8", "18:30", "19:00", "half 6", "noon", "9:15", "20:00", "17:45", "10", "13:30", "21:00"),
    "place": ("the library", "the gym", "the station", "the cafe", "campus", "the market", "the clinic", "Mama's",
              "the park", "the cinema", "the canteen", "the bus stop", "Room 204", "the lab", "the hostel"),
    "food": ("rice", "bread", "milk", "eggs", "tomatoes", "noodles", "bananas", "coffee", "onions", "yogurt",
             "lentils", "mangoes"),
    "item": ("charger", "umbrella", "jacket", "headphones", "notebook", "water bottle", "keys", "laptop bag"),
    "gift": ("phone", "tablet", "holiday", "gift card", "laptop", "TV"),
    "prize": ("first prize", "second prize", "gift basket", "bicycle", "book voucher"),
    "shop": ("City Market", "Corner Books", "Green Grocer", "Tech Corner", "Style Street"),
    "amount": ("500", "1,000", "2,500", "5,000", "10,000", "250"),
    "small_amount": ("5", "10", "15", "20", "50"),
    "fee": ("1.99", "2.50", "3.00", "4.99", "0.99", "12.40", "23.75"),
    "pct": ("20", "30", "50", "70"),
}
SPAM_DOMAINS = ("claim-prize.example", "secure-verify.example", "parcel-track.example", "easy-loan.example",
                "bonus-now.example", "tax-refund.example", "crypto-x.example", "deals4u.example")
SERVICE_DOMAINS = ("parcel-post.example", "my-bank.example", "citymarket.example", "mobile-co.example",
                   "delivery-hub.example")
TEXTING = ((r"\byou\b", "u"), (r"\bare\b", "r"), (r"\btomorrow\b", "2moro"), (r"\b[Pp]lease\b", "pls"),
           (r"\bthanks\b", "thx"), (r"\bsee\b", "c"), (r"\btonight\b", "2nite"), (r"\bminutes\b", "mins"))


def sms_fill(rng: Rng, template: str) -> str:
    def choice(options: Sequence[str]) -> str:
        return options[int(rng.integers(len(options)))]

    def slug() -> str:
        return "".join(choice("abcdefghijkmnpqrstuvwxyz23456789") for _ in range(5))

    values = {key: choice(options) for key, options in SMS_SLOTS.items()}
    values.update(name=choice(FIRST_NAMES), name2=choice(FIRST_NAMES), food2=choice(SMS_SLOTS["food"]),
                  num=str(int(rng.integers(2, 40))), small_num=str(int(rng.integers(0, 6))),
                  code=f"{int(rng.integers(100_000, 1_000_000))}", short=str(int(rng.integers(60_000, 90_000))),
                  phone=f"0800 {int(rng.integers(100, 1000))} {int(rng.integers(1000, 10_000))}",
                  url=f"{choice(('http://', 'https://', ''))}{choice(SPAM_DOMAINS)}/{slug()}",
                  link=f"{choice(('https://', ''))}{choice(SERVICE_DOMAINS)}/{slug()}")
    return template.format(**values)


def make_sms(rng: Rng) -> Files:
    """M18-L05: 2,400 synthetic text messages labelled ham or spam (15% spam).

    Not the UCI SMS Spam Collection: every message comes from the templates above. Planted overlap, so no
    classifier is perfect: service notices (parcels, codes, bills, shop offers, a raffle) come in wanted and
    unwanted versions that read the same, as smishing copies real notices; ham uses spam-like words in
    innocent ways (free, win, prize, urgent, money, claim, offer); some spam avoids the classic trigger words
    (the "lost my phone" and wrong-number scams). Texting style varies (lower case, "u", "2moro", no final
    punctuation, openers and emoji). Links use reserved .example domains.
    """
    n_ham, n_spam = 2040, 360
    weights = np.array([p for _, p in SERVICE])
    messages = []
    for label, n in (("ham", n_ham), ("spam", n_spam)):
        for _ in range(n):
            if rng.random() < (0.035 if label == "ham" else 0.11):
                w = weights if label == "ham" else 1 - weights
                text = sms_fill(rng, SERVICE[int(rng.choice(len(SERVICE), p=w / w.sum()))][0])
            elif label == "ham":
                opener, body = HAM_OPENERS[int(rng.integers(len(HAM_OPENERS)))], HAM[int(rng.integers(len(HAM)))]
                if opener and not opener.endswith("! ") and not re.match(r"I\b|I'", body):
                    body = body[0].lower() + body[1:]
                if rng.random() < 0.15:     # two messages in one
                    joint = " " if body[-1] in ".!?" or not body[-1].isascii() else ". "
                    body += joint + HAM[int(rng.integers(len(HAM)))]
                text = sms_fill(rng, opener + body + HAM_CLOSERS[int(rng.integers(len(HAM_CLOSERS)))])
                if rng.random() < 0.25:
                    for pattern, short in TEXTING:
                        text = re.sub(pattern, short, text)
            else:
                text = sms_fill(rng, SPAM[int(rng.integers(len(SPAM)))]
                                + SPAM_CLOSERS[int(rng.integers(len(SPAM_CLOSERS)))])
            if rng.random() < (0.3 if label == "ham" else 0.1):
                text = text.lower()
            if label == "spam" and rng.random() < 0.15:
                text = text.upper()
            if rng.random() < 0.2:
                text = text.rstrip(".!?")
            messages.append((label, text))
    order = rng.permutation(len(messages))
    rows = [(k + 1, *messages[i]) for k, i in enumerate(order)]
    texts = [text for _, text in messages]
    assert len(texts) - len(set(texts)) < 0.1 * len(texts), "too many duplicate messages"
    return {"sms_small.csv": csv_bytes(("id", "label", "text"), rows)}


# ----------------------------------------------------------------------------- books and ratings
GENRES = ("fantasy", "science fiction", "mystery", "romance", "history", "science", "business", "self-help",
          "poetry", "children", "cooking", "travel")
TITLES = {  # genre: (templates, words for {a}, words for {b})
    "fantasy": (("The {a} {b}", "{b} of the {a} Moon"), ("Silver", "Hidden", "Broken", "Burning", "Forgotten",
                "Crimson", "Sleeping", "Iron", "Glass", "Shadow"), ("Crown", "Gate", "Forest", "Dragon", "Kingdom",
                "Tower", "Sword", "River", "Throne", "Map")),
    "science fiction": (("{a} {b}", "The {b} Protocol", "Beyond the {b}"), ("Orbit", "Station", "Colony", "Signal",
                        "Quantum", "Deep"), ("Horizon", "Nebula", "Machine", "Drift", "Echo", "Frontier", "Archive",
                        "Equinox", "Relay", "Lattice")),
    "mystery": (("The {a} {b}", "Death at {b}", "The {b} Affair"), ("Silent", "Missing", "Second", "Locked",
                "Midnight", "Last"), ("Witness", "Harbour House", "Key", "Lighthouse", "Garden", "Letter", "Station",
                "Orchard", "Clocktower", "Ferry", "Bridge", "Pier", "Museum", "Vineyard", "Observatory")),
    "romance": (("{a} in {b}", "Letters from {b}", "The {a} Promise"), ("Summer", "Spring", "Rain", "Winter",
                "Sunrise", "Moonlight"), ("Lisbon", "Kyoto", "Nairobi", "Valparaíso", "Hanoi", "Marrakesh",
                "Istanbul", "Zanzibar", "Oaxaca", "Penang")),
    "history": (("A History of {b}", "The Age of {b}", "{b}: A Global History"), ("",), ("Salt", "Maps", "Clocks",
                "Bridges", "Paper", "Spices", "Railways", "Cotton", "Ports", "Coins", "Libraries", "Rice", "Glass",
                "Tea", "Silk", "Sugar", "Bicycles", "Lighthouses", "Markets", "Bread", "Numbers", "Ink")),
    "science": (("The Science of {b}", "Why {b} Matters", "Inside the {a} {b}"), ("Hidden", "Living", "Secret",
                "Invisible"), ("Sleep", "Soil", "Rivers", "Bees", "Light", "Volcanoes", "Memory", "Clouds", "Forests",
                "Oceans")),
    "business": (("{a} Rules for {b}", "The {b} Playbook", "Leading {b}"), ("Seven", "Ten", "Twelve", "Five"),
                 ("Small Teams", "Startups", "Remote Work", "Hard Decisions", "Pricing", "Growth", "Meetings",
                  "Negotiation", "Customer Service", "Hiring")),
    "self-help": (("The Art of {b}", "{a} Habits", "Making Time for {b}", "Small Steps to {b}", "The {a} Mind"),
                  ("Better", "Quiet", "Small", "Kind", "Simple", "Calm", "Curious", "Patient"),
                  ("Listening", "Rest", "Focus", "Saying No", "Starting Over", "Patience", "Learning", "Gratitude",
                   "Walking", "Writing", "Sleep", "Courage", "Kindness", "Balance", "Change")),
    "poetry": (("Poems from the {b}", "{a} and {b}", "Songs of the {b}"), ("Salt", "Dust", "Rain", "Ash", "Honey"),
               ("Coast", "Valley", "Desert", "City", "Mountains", "Delta", "Island", "Harbour", "Steppe", "Lake")),
    "children": (("{name} and the {a} {b}", "The {a} {b}"), ("Brave", "Tiny", "Sleepy", "Clever", "Lost", "Happy"),
                 ("Elephant", "Turtle", "Kite", "Robot", "Dragon", "Penguin", "Lion", "Balloon", "Fox", "Owl")),
    "cooking": (("Cooking with {b}", "The {a} Kitchen", "{b} Every Day", "A Year of {b}", "{a} Recipes"),
                ("Street Food", "Family", "Market", "Coastal", "Mountain", "Weeknight", "Garden", "Village"),
                ("Rice", "Beans", "Lentils", "Spices", "Corn", "Coconut", "Noodles", "Vegetables", "Bread", "Yogurt",
                 "Tomatoes", "Chillies", "Mushrooms", "Fish", "Eggs")),
    "travel": (("{a} Days in {b}", "Walking {b}", "On the Road in {b}"), ("Ten", "Seven", "Thirty", "Forty"),
               ("Patagonia", "the Andes", "Rajasthan", "the Balkans", "Anatolia", "the Mekong", "the Atlas Mountains",
                "Lapland", "the Pampas", "Borneo")),
}


def make_book_ratings(rng: Rng) -> Files:
    """M18-L08 (and elective E6, capstone track 4): a fictional online bookstore's catalogue and star ratings.

    books.csv: 400 books in 12 genres. ratings.csv: about 30,000 ratings (1-5 stars) from 900 users, each
    user rating a book at most once, with a timestamp (2024-01 to 2026-09) for time-based splits. Planted:
    users have genre preferences and personal rating biases; books have a quality and a popularity (a long
    tail); users mostly rate books in genres they like (missing not at random); ratings also follow three
    hidden "style" factors that matrix factorisation can recover.
    """
    n_books, n_users = 400, 900
    authors = unique_names(rng, 230)
    author_genres = [rng.choice(12, 2, replace=False) for _ in authors]
    genre_of = rng.choice(12, n_books, p=np.array([12, 9, 11, 9, 7, 6, 6, 6, 4, 8, 7, 6]) / 91)
    titles: set[str] = set()
    books = []
    for b in range(n_books):
        genre = GENRES[genre_of[b]]
        templates, first, second = TITLES[genre]
        for _ in range(1000):
            title = templates[int(rng.integers(len(templates)))].format(
                a=first[int(rng.integers(len(first)))], b=second[int(rng.integers(len(second)))],
                name=FIRST_NAMES[int(rng.integers(len(FIRST_NAMES)))]).replace("  ", " ").strip()
            if title not in titles:
                titles.add(title)
                break
        else:
            raise RuntimeError(f"not enough different {genre} titles: add words to TITLES")
        writers = [k for k, g in enumerate(author_genres) if genre_of[b] in g]
        author = authors[writers[int(rng.integers(len(writers)))]]
        year = int(max(1950, 2026 - np.floor(rng.gamma(1.5, 8))))
        pages = int(np.clip(rng.normal({"children": 48, "poetry": 110, "cooking": 220}.get(genre, 320), 60), 24, 900))
        books.append((b + 1, title, author, genre, year, pages))
    preference = rng.dirichlet(np.full(12, 0.5), n_users)
    popularity = rng.lognormal(0, 1.0, n_books)
    quality = rng.normal(0, 0.45, n_books)
    style_user, style_book = rng.normal(0, 0.45, (n_users, 3)), rng.normal(0, 0.45, (n_books, 3))
    bias = rng.normal(0, 0.35, n_users)
    count = np.clip(np.round(rng.lognormal(np.log(25), 0.8, n_users)), 3, 250).astype(int)
    joined = rng.integers(0, (date(2026, 6, 30) - date(2024, 1, 1)).days, n_users)
    end = datetime(2026, 9, 30, 23, 59, 59)
    rows = []
    for u in range(n_users):
        affinity = preference[u, genre_of]
        weight = popularity ** 0.9 * np.exp(3.0 * affinity)
        items = rng.choice(n_books, min(count[u], n_books), replace=False, p=weight / weight.sum())
        latent = (3.45 + bias[u] + quality[items] + 2.0 * (affinity[items] - 1 / 12)
                  + style_book[items] @ style_user[u] + rng.normal(0, 0.55, items.size))
        stars = np.clip(np.round(latent), 1, 5).astype(int)
        first = datetime(2024, 1, 1) + timedelta(days=int(joined[u]))
        span = int((end - first).total_seconds())
        times = sorted(first + timedelta(seconds=int(s)) for s in rng.integers(0, span, items.size))
        rows += [(u + 1, int(i) + 1, int(s), stamp(t)) for i, s, t in zip(items, stars, times, strict=True)]
    assert 25_000 < len(rows) < 36_000 and len({(r[0], r[1]) for r in rows}) == len(rows), len(rows)
    return {"books.csv": csv_bytes(("book_id", "title", "author", "genre", "year", "pages"), books),
            "ratings.csv": csv_bytes(("user_id", "book_id", "rating", "rated_at"), rows)}


# ----------------------------------------------------------------------------- GloVe subset (not seeded)
GLOVE_MEMBER = "glove.6B.50d.txt"
GLOVE_TOP = 2000      # the most frequent purely alphabetic words, in the file's frequency order
GLOVE_WORDS = """
king queen man woman men women boy girl boys girls father mother son daughter brother sister husband wife uncle
aunt nephew niece prince princess actor actress he she him her his hers mr mrs grandfather grandmother emperor
empress waiter waitress gentleman lady male female boyfriend girlfriend
paris france berlin germany rome italy madrid spain lisbon portugal london britain england tokyo japan beijing
china moscow russia delhi india cairo egypt nairobi kenya abuja nigeria accra ghana dakar senegal kampala uganda
kigali rwanda lusaka zambia harare zimbabwe ottawa canada canberra australia lima peru bogota colombia quito
ecuador santiago chile caracas venezuela havana cuba ankara turkey tehran iran baghdad iraq kabul afghanistan
islamabad pakistan dhaka bangladesh kathmandu nepal bangkok thailand hanoi vietnam manila philippines jakarta
indonesia seoul korea athens greece warsaw poland vienna austria brussels belgium amsterdam netherlands dublin
ireland oslo norway stockholm sweden helsinki finland copenhagen denmark budapest hungary bucharest romania doha
qatar beirut lebanon damascus syria amman jordan rabat morocco tunis tunisia algiers algeria khartoum sudan
french german italian spanish portuguese british english japanese chinese russian indian egyptian kenyan nigerian
ghanaian canadian australian peruvian colombian chilean cuban turkish iranian iraqi afghan pakistani bangladeshi
nepalese thai vietnamese filipino indonesian korean greek polish austrian belgian dutch irish norwegian swedish
finnish danish hungarian romanian moroccan arabic hindi swahili
walk walked walking walks swim swam swimming go went going goes run ran running write wrote written writing eat
ate eaten eating see saw seen seeing take took taken taking speak spoke spoken speaking sing sang sung singing fly
flew flown flying drive drove driven driving buy bought buying think thought thinking play played playing read
reading know knew known give gave given come came coming
good better best bad worse worst big bigger biggest small smaller smallest fast faster fastest slow slower slowest
strong stronger strongest young younger youngest old older oldest long longer longest short shorter shortest tall
taller tallest high higher highest low lower lowest cheap cheaper cheapest easy easier easiest hard harder hardest
large larger largest great greater greatest warm warmer warmest cold colder coldest
cat cats dog dogs car cars city cities child children mouse mice person people apple apples computer computers
house houses tree trees bird birds country countries
horse cow sheep goat pig lion tiger elephant monkey fish snake wolf bear rabbit eagle shark whale frog camel zebra
giraffe banana orange mango grape lemon cherry peach pear strawberry pineapple watermelon papaya coconut carrot
potato tomato onion garlic cabbage lettuce spinach cucumber pepper red blue green yellow black white purple pink
brown grey gray one two three four five six seven eight nine ten hundred thousand million billion monday tuesday
wednesday thursday friday saturday sunday january february march april may june july august september october
november december football soccer cricket tennis basketball baseball hockey golf rugby cycling volleyball
doctor nurse teacher engineer programmer scientist lawyer pilot chef farmer soldier police firefighter accountant
architect artist musician writer journalist secretary receptionist homemaker librarian dancer designer manager
carpenter plumber electrician mechanic cashier cleaner surgeon dentist pharmacist professor student banker
economist judge mathematician physicist chemist biologist hairdresser nanny maid
bus train plane bicycle truck ship boat motorcycle taxi subway software hardware internet algorithm data database
network python java programming code keyboard laptop phone robot website email happy sad angry afraid excited calm
proud lonely anxious piano guitar violin drum flute trumpet physics chemistry biology mathematics astronomy geology
economics rain snow wind storm sunny cloudy fog head hand foot eye ear nose mouth heart brain bread rice pasta
cheese coffee tea milk sugar salt pizza noodles soup chocolate cake bank bat bass crane jaguar amazon spring rock
light match
""".split()  # noqa: SIM905 - the word list reads better as text


def glove_lines(path: Path) -> Iterator[str]:
    """Lines of glove.6B.50d.txt, read from the text file or straight out of glove.6B.zip."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf, zf.open(GLOVE_MEMBER) as raw:
            yield from io.TextIOWrapper(raw, encoding="utf-8")
    else:
        with path.open(encoding="utf-8") as f:
            yield from f


def glove_subset(lines: Iterable[str], top: int = GLOVE_TOP, words: Iterable[str] = GLOVE_WORDS) -> bytes:
    """The `top` most frequent alphabetic words plus `words`, in frequency order, as JSON {word: [floats]}.

    Values are rounded to 4 decimals. Fails if any of `words` is missing, so the list stays honest.
    """
    wanted = set(words)
    found: set[str] = set()
    rows: list[str] = []
    frequent, dims = 0, None
    for line in lines:
        word, *values = line.rstrip("\n").split(" ")
        dims = dims or len(values)
        if len(values) != dims:
            continue
        common = frequent < top and word.isascii() and word.isalpha()
        if not common and word not in wanted:
            continue
        frequent += common
        found.add(word)
        numbers = ", ".join(repr(round(float(v), 4) or 0.0) for v in values)
        rows.append(f"  {json.dumps(word)}: [{numbers}]")
        if frequent >= top and found >= wanted:
            break
    if wanted - found:
        raise ValueError(f"not in the GloVe vocabulary: {' '.join(sorted(wanted - found))}")
    return ("{\n" + ",\n".join(rows) + "\n}\n").encode("utf-8")


# ----------------------------------------------------------------------------- registry
@dataclass(frozen=True)
class Dataset:
    name: str
    seed: int
    make: Callable[[Rng], Files]
    used_by: str


DATASETS = (
    Dataset("server_logs", 101, make_server_logs, "M05-L04, M05 project, M06-L01"),
    Dataset("server_logs_large", 102, make_server_logs_large, "M08-L02, M08 project, M10-L05"),
    Dataset("images", 111, make_images, "M11-L05, M11 project, E2"),
    Dataset("shop", 121, make_shop, "M12, M13-L01, M15-L01 to L03"),
    Dataset("food_delivery", 131, make_food_delivery, "M12-L04, M12 project, M15, P3"),
    Dataset("student_performance", 141, make_student_performance, "M13-L03, M13-L04, M14"),
    Dataset("housing", 161, make_housing, "M16-L03, M16 project"),
    Dataset("telco_churn", 171, make_telco_churn, "M17, M19, P4, M24, M25-L06, P6"),
    Dataset("transactions_fraud", 181, make_transactions_fraud, "M16-L07, M17-L07, M25-L07"),
    Dataset("sms", 191, make_sms, "M18-L05"),
    Dataset("book_ratings", 201, make_book_ratings, "M18-L08, E6, capstone"),
)


def generate(names: Iterable[str] | None = None) -> Files:
    """Every file of the chosen datasets (default: all), as {file name: bytes}."""
    chosen = set(names) if names else {d.name for d in DATASETS}
    files: Files = {}
    for dataset in DATASETS:
        if dataset.name in chosen:
            made = dataset.make(np.random.default_rng(dataset.seed))
            if set(made) & set(files):
                raise ValueError(f"{dataset.name}: file name already used: {sorted(set(made) & set(files))}")
            files.update(made)
    too_big = {name: len(data) for name, data in files.items() if len(data) > MAX_BYTES}
    if too_big:
        raise ValueError(f"over {MAX_BYTES:,} bytes: {too_big}")
    return files


def shape(name: str, data: bytes) -> str:
    """A short description of a file's contents, as the README states it."""
    if name.endswith(".csv"):
        rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
        return f"{len(rows) - 1:,} rows × {len(rows[0])} columns"
    if name.endswith(".txt"):
        lines = data.count(b"\n")
        return f"{lines:,} lines"
    if name.endswith(".db"):
        conn = sqlite3.connect(":memory:")
        try:
            conn.deserialize(data)
            tables = [t for (t,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY rowid")]
            return ", ".join(f"{t} {conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,}" for t in tables)
        finally:
            conn.close()
    if name.endswith(".npz"):
        with np.load(io.BytesIO(data)) as npz:
            return ", ".join(f"{k} {npz[k].shape}" for k in npz.files)
    obj = json.loads(data)
    if isinstance(obj, dict) and len(obj) == 1:
        (key, value), = obj.items()
        return f"{len(value):,} {key}"
    return f"{len(obj):,} entries"


def compare(files: Files, folder: Path) -> list[str]:
    """Problems that make folder differ from files: missing, changed or unexpected files."""
    problems = []
    for name, data in files.items():
        path = folder / name
        if not path.exists():
            problems.append(f"{name}: missing")
        elif name.endswith(".db") and sqlite_dump(path.read_bytes()) != sqlite_dump(data):
            problems.append(f"{name}: tables differ from a fresh run")
        elif not name.endswith(".db") and path.read_bytes() != data:
            problems.append(f"{name}: bytes differ from a fresh run")
    for path in sorted(folder.iterdir()) if folder.exists() else []:
        if path.name not in files and path.name not in NOT_GENERATED and not path.name.startswith("."):
            problems.append(f"{path.name}: not made by make_datasets.py")
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="datasets to build (default: all)")
    ap.add_argument("--out", type=Path, default=DATA, help="output folder (default: site/data)")
    ap.add_argument("--list", action="store_true", help="describe the datasets instead of writing them")
    ap.add_argument("--check", action="store_true", help="exit 1 if the output folder differs from a fresh run")
    ap.add_argument("--glove", type=Path, metavar="PATH", help="glove.6B.zip or glove.6B.50d.txt")
    args = ap.parse_args(argv)
    unknown = set(args.names) - {d.name for d in DATASETS}
    if unknown:
        ap.error(f"unknown dataset(s): {', '.join(sorted(unknown))}; see --list")
    files = generate(args.names)
    if args.list:
        for dataset in DATASETS:
            if not args.names or dataset.name in args.names:
                made = dataset.make(np.random.default_rng(dataset.seed))
                print(f"{dataset.name} (seed {dataset.seed}; {dataset.used_by})")
                for name, data in made.items():
                    print(f"  {name:32} {len(data) / 1000:8,.1f} KB  {shape(name, data)}")
        return 0
    if args.check:
        problems = compare(files, args.out)
        for problem in problems:
            print(f"  {problem}")
        print(f"make_datasets --check: {len(files)} file(s), {len(problems)} problem(s)")
        if problems:
            print("Run: python tools/make_datasets.py")
        return 1 if problems else 0
    args.out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (args.out / name).write_bytes(data)
    if args.glove:
        data = glove_subset(glove_lines(args.glove))
        (args.out / "glove-mini.json").write_bytes(data)
        print(f"wrote glove-mini.json ({len(data) / 1000:,.1f} KB, {data.count(b': [')} words)")
    total = sum(len(d) for d in files.values())
    print(f"make_datasets: wrote {len(files)} file(s) to {args.out}, {total / 1e6:.2f} MB in all, "
          f"largest {max(len(d) for d in files.values()) / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
