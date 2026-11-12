import random
import time
import httpx

# этот скрипт гонит данные из 2gis/tbank/sber в один формат для удобства
# {
#     "id": "12345",                    # ID заправки (строка)
#     "name": "Газпромнефть",           # Название
#     "address": "ул. Ленина, д. 10",   # Адрес
#     "lat": 55.45, "lon": 47.52,       # Координаты (числа)
#     "fuels": {                        # Наличие видов топлива:
#         "АИ-92": "yes",               # 'yes' (Есть), 'no' (Нет),
#         "АИ-95": "maybe",             # 'maybe' (Возможно),
#         "ДТ": "unknown",              # 'unknown' (Н/Д)
#         "Газ": "no",
#         "АИ-98": "unknown"
#     }
# }

# формат координат {мин. широта, макс. широта, мин. долгота, макс. долгота}
bbox = (55.445343, 55.553948, 47.414038, 47.581899)

# меньше этого область не делим
min_cell = 0.005

# виды топлива как в настройках
fuel_names = ("АИ-92", "АИ-95", "ДТ", "Газ", "АИ-98")

# наличие (бекенд)
y = "yes"
n = "no"
m = "maybe"
u = "unknown"

# наличие (в таблицу)
labels = {y: "Есть", n: "Нет", m: "Возможно", u: "Н/Д"}

# для склейки видов газа (сбер отдает несколько)
order = [y, m, n, u]

tbank_status = {
    "available": y,
    "not_available": n,
    "maybe_available": m,
    "maybe_not_available": m,
}


# стоп (из ui)
class Stopped(Exception):
    pass


# лог и остановка (tick дает окну обновиться)
class Logger:
    def __init__(self, log, tick):
        self.log = log
        self.tick = tick
        self.stopped = False

    def stop(self):
        self.stopped = True

    def check(self):
        self.tick()

        if self.stopped:
            raise Stopped()

    def pause(self, seconds):
        end = time.time() + seconds

        while time.time() < end:
            self.check()
            time.sleep(0.05)


# клиент
def make_client(verify=True):
    return httpx.Client(timeout=httpx.Timeout(10, connect=5),
                        follow_redirects=True, verify=verify)


def make_headers(base):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": base,
        "Referer": base + "/",
    }


# запрос и json, 4 попытки (ВНИМАНИЕ: С ВПН НЕ РАБОТАЕТ)
def get_json(job, client, url, params, base):
    for attempt in range(1, 5):
        job.pause(random.uniform(0.3, 1.0))

        try:
            response = client.get(url, params=params, headers=make_headers(base))
        except httpx.HTTPError as e:
            job.log(f"Запрос не удался ({attempt}/4): {e}")
            job.pause(2 * attempt)
            continue

        if response.status_code == 400:
            return None

        if response.status_code == 429:
            job.pause(5 * attempt)
            continue

        if response.status_code != 200:
            job.log(f"Ответ {response.status_code} ({attempt}/4)")
            job.pause(2 * attempt)
            continue

        try:
            return response.json()
        except ValueError:
            job.log("Ответ не является JSON")
            return None

    return None


# делит область на 4 части
def split_bbox(cell):
    min_lat, max_lat, min_lon, max_lon = cell
    mid_lat = (min_lat + max_lat) / 2
    mid_lon = (min_lon + max_lon) / 2

    return [
        (min_lat, mid_lat, min_lon, mid_lon),
        (min_lat, mid_lat, mid_lon, max_lon),
        (mid_lat, max_lat, min_lon, mid_lon),
        (mid_lat, max_lat, mid_lon, max_lon),
    ]


def cell_size(cell):
    min_lat, max_lat, min_lon, max_lon = cell
    height = max_lat - min_lat
    width = max_lon - min_lon
    return max(height, width)


def text(value):
    if value is None:
        return ""

    return str(value)


def as_list(value):
    if value is None:
        return []

    return value


def better(a, b):
    if order.index(a) <= order.index(b):
        return a

    return b


# AI_92, ai92, 92, DT, diesel, GAS -> название из fuel_names (ai100 склеиваем с АИ-98, прочее пропускаем)
def canon_fuel(raw):
    s = text(raw).lower()
    s = s.replace("-", "").replace("_", "").replace(" ", "")

    if s.startswith("ai"):
        s = s[2:]

    if s in ("92", "95"):
        return "АИ-" + s

    # АИ-98 и АИ-100 идут одной строкой
    if s in ("98", "100"):
        return "АИ-98"

    if s in ("dt", "diesel"):
        return "ДТ"

    if s in ("gas", "propane", "methane"):
        return "Газ"

    return None


# pairs это список (сырое название топлива, статус)
def make_row(ext_id, name, address, lat, lon, pairs, station_status=None):
    fuels = {}

    for fuel in fuel_names:
        fuels[fuel] = u

    for raw_fuel, status in pairs:
        fuel = canon_fuel(raw_fuel)

        if fuel is None:
            continue

        fuels[fuel] = better(fuels[fuel], status)

    return {
        "id": text(ext_id),
        "name": text(name),
        "address": text(address),
        "lat": lat,
        "lon": lon,
        "fuels": fuels,
        "status": station_status,
    }


# общий статус АЗС у 2ГИС -> наш (так красит кружки их сайт)
gis2_station_status = {
    "AVAILABLE": y,
    "PARTIALLY_AVAILABLE": m,
    "NOT_AVAILABLE": n,
    "NO_DATA": u,
}


def normalize_gis2(items):
    rows = []

    for item in items:
        station = item["station"]
        pairs = []

        for fuel_status in as_list(item.get("fuel_statuses")):
            available = fuel_status.get("available")

            if available is True:
                status = y
            elif available is False:
                status = n
            else:
                status = u

            pairs.append((fuel_status.get("fuel_type"), status))

        row = make_row(station.get("id"), station.get("name"), station.get("address"),
                       station.get("lat"), station.get("lng"), pairs,
                       gis2_station_status.get(item.get("status"), u))
        rows.append(row)

    return rows


def normalize_tbank(items):
    rows = []

    for item in items:
        pairs = []
        by_fuel = item.get("statusByFuelType")

        if by_fuel is None:
            by_fuel = {}

        for raw_fuel, raw_status in by_fuel.items():
            status = tbank_status.get(raw_status, u)
            pairs.append((raw_fuel, status))

        row = make_row(item.get("id"), item.get("name"), item.get("addr"),
                       item.get("lat"), item.get("lon"), pairs)
        rows.append(row)

    return rows


def sber_status(fuel):
    value = fuel.get("availabilityStatus")

    if value == "available":
        return y

    if value == "unavailable":
        return n

    if value == "not_available":
        return n

    if value == "stale":
        return m

    # явное "unknown" — на сайте это Н/Д, даже если рядом стоит available: true
    if value == "unknown":
        return u

    available = fuel.get("available")

    if available is True:
        return y

    if available is False:
        return n

    return u


def normalize_sber(items):
    rows = []

    for item in items:
        location = item.get("location")

        if location is None:
            location = {}

        pairs = []

        for fuel in as_list(item.get("fuels")):
            pairs.append((fuel.get("type"), sber_status(fuel)))

        row = make_row(item.get("id"), item.get("name"), item.get("address"),
                       location.get("lat"), location.get("lon"), pairs)
        rows.append(row)

    return rows
