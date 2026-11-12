from .parser import bbox, cell_size, get_json, make_client, min_cell, split_bbox

# формат ответа 2gis
# [
#   {
#     "station": {"id": "70000001062762978", "name": "АЗС", "address": "Канаш (...), Канашская улица, 38", "lat": 55.515061, "lng": 47.496553},
#     "status": "PARTIALLY_AVAILABLE",
#     "fuel_statuses": [
#       {"fuel_type": "AI_92", "available": true, "queue_level": "NONE", "last_report_at": "2026-07-28T19:37:54Z"}
#     ],
#     "prices": []
#   },
#   {"count": 5}
# ]
# fuel_type бывает AI_92, AI_95, AI_98, AI_100, DT, GAS
# available бывает true, false или null (нет данных)
# fuel_statuses бывает null, тогда данных по топливу нет
# запрос: get /api/v1/stations?minLon=&minLat=&maxLon=&maxLat=

base = "https://benzin.api.2gis.ru"
url = base + "/api/v1/stations"


# проверка на кластер (это много станций в одной точке)
def is_cluster(item):
    if "count" in item:
        return True

    station = item.get("station")

    if not station:
        return True

    if not station.get("id"):
        return True

    return False


# скачивает станции, кластер не берем
def fetch(job):
    found = {}
    cells = [bbox]

    with make_client() as client:
        while len(cells) > 0:
            job.check()
            cell = cells.pop()

            if cell_size(cell) < min_cell:
                continue

            min_lat, max_lat, min_lon, max_lon = cell
            params = {"minLon": min_lon, "minLat": min_lat,
                      "maxLon": max_lon, "maxLat": max_lat}
            data = get_json(job, client, url, params, base)

            if not isinstance(data, list):
                continue

            has_cluster = False

            for item in data:
                if is_cluster(item):
                    has_cluster = True
                    continue

                station_id = str(item["station"]["id"])
                found[station_id] = item

            job.log(f"2ГИС: найдено {len(found)}")

            if has_cluster:
                cells.extend(split_bbox(cell))

    return list(found.values())
