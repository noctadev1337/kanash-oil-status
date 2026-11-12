from .parser import bbox, cell_size, get_json, make_client, min_cell, split_bbox

# формат ответа сбера
# {
#   "stations": [
#     {
#       "id": "70000001032869063",
#       "name": "Татнефть, АЗС",
#       "address": "Чувашская Республика, д. Малые Бикшихи, 294",
#       "location": {"lat": 55.485, "lon": 47.480734},
#       "availabilityStatus": "available",
#       "fuels": [
#         {"type": "ai92", "available": true, "availabilityStatus": "available", "limitLiters": 30}
#       ]
#     }
#   ]
# }
# type бывает ai80, ai92, ai95, ai98, ai100, diesel, methane, propane
# availabilityStatus бывает available, stale (возможно), unknown или его нет совсем
# газ у них это methane и propane, в таблице они оба идут в "газ"
# запрос: get /api/stations?bbox=minLon,minLat,maxLon,maxLat (долгота идет первой)

base = "https://sberazs.ru"
url = base + "/api/stations"


# скачивает станции, нормализация в parser.py
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
            params = {"bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}"}
            data = get_json(job, client, url, params, base)

            if not isinstance(data, dict):
                continue

            stations = data.get("stations")

            if stations is None:
                continue

            for item in stations:
                station_id = item.get("id")

                if station_id is None:
                    continue

                found[str(station_id)] = item

            job.log(f"Сбер АЗС: найдено {len(found)}")

    return list(found.values())
