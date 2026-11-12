from .parser import bbox, cell_size, get_json, make_client, min_cell, split_bbox

# формат ответа т-банка
# {
#   "status": "ok",
#   "payload": [
#     {
#       "id": "...", "name": "...", "brand": "...", "addr": "...", "lat": 55.5, "lon": 47.4,
#       "status": "available",
#       "statusByFuelType": {"92": "available", "95": "maybe_available", "100": "no_data", "diesel": "not_available"},
#       "priceByFuelType": {"92": 58.1},
#       "lastTransactionAt": "...",
#       "confidence": 0.85
#     }
#   ]
# }
# статусы бывают available, maybe_available, maybe_not_available, not_available, no_data
# если status не ok, ответ пропускаем
# сертификата у тиньки нет, поэтому проверку ssl отключаем
# запрос: get /api/v1/stations?minLat=&maxLat=&minLon=&maxLon=

base = "https://toplivo.tbank.ru"
url = base + "/api/v1/stations"


# скачивает станции, нормализация в parser.py
def fetch(job):
    found = {}
    cells = [bbox]

    with make_client(verify=False) as client:
        while len(cells) > 0:
            job.check()
            cell = cells.pop()

            if cell_size(cell) < min_cell:
                continue

            min_lat, max_lat, min_lon, max_lon = cell
            params = {"minLat": min_lat, "maxLat": max_lat, "minLon": min_lon, "maxLon": max_lon}
            data = get_json(job, client, url, params, base)

            if not isinstance(data, dict):
                continue

            if data.get("status") != "ok":
                continue

            payload = data.get("payload")  # json

            if payload is None:
                payload = []

            for item in payload:
                station_id = item.get("id")

                if station_id is None:
                    continue

                found[station_id] = item

            job.log(f"Т-Банк: найдено {len(found)}")

    return list(found.values())
