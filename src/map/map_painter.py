from PIL import Image, ImageDraw, ImageFont

STATUS_ORDER = ("yes", "maybe", "no", "unknown")

fuel_labels = {
    "yes": "В наличии",
    "no": "Отсутствует",
    "maybe": "Возможно",
    "unknown": "Неизвестно",
}

oil_status = [
    ("#2ecc71", "Топливо в наличии"),
    ("#f39c12", "Возможно есть"),
    ("#e74c3c", "Нет топлива"),
    ("#95a5a6", "Нет данных"),
]

COLORS = [item[0] for item in oil_status]
border_gray = "#595959"
inner_white = "#ffffff"
gray_color = COLORS[3]  # серый по умолчанию / нет данных

# точки карты с жёсткими названиями и расположением плашки
stations = [
    {"id": "bashneft", "x": 265, "y": 144, "name": "Башнефть", "label_pos": "left",
     "name_patterns": [["башнефть"]], "addr_patterns": [[]]},
    {"id": "gazprom", "x": 316, "y": 173, "name": "Газпромнефть", "label_pos": "bottom",
     "name_patterns": [["газпромнефть"]], "addr_patterns": [[]]},
    {"id": "tatneft_65", "x": 360, "y": 102, "name": "Татнефть №65", "label_pos": "right",
     "name_patterns": [["татнефть"]], "addr_patterns": [["кооператив", "16"]]},
    {"id": "lukoil", "x": 554, "y": 148, "name": "Лукойл", "label_pos": "bottom_left",
     "name_patterns": [["лукойл"]], "addr_patterns": [[]]},
    {"id": "quickstop", "x": 631, "y": 134, "name": "QuickStop", "label_pos": "bottom",
     "name_patterns": [["квикстоп"], ["quickstop"]], "addr_patterns": [[]]},
    {"id": "tat_ekonom", "x": 696, "y": 110, "name": "Тат-эконом", "label_pos": "right",
     "name_patterns": [[]], "addr_patterns": [["канашская улица, 38"]]},
    {"id": "tatneft_67", "x": 1208, "y": 243, "name": "Татнефть №67", "label_pos": "bottom",
     "name_patterns": [["татнефть"]], "addr_patterns": [["янтиковское шоссе, 58"]]},
    {"id": "econom_azs", "x": 995, "y": 218, "name": "Эко-ном АЗС", "label_pos": "top",
     "name_patterns": [["эконом"], ["эко-ном"], ["эко ном"], ["азс"]],
     "addr_patterns": [["янтиковское шоссе, 15"], ["ильича"]]},
    # №66 это верхний кружок, №68 нижний (запись без улицы)
    {"id": "tatneft_66", "x": 513, "y": 731, "name": "Татнефть №66", "label_pos": "top_right",
     "name_patterns": [["татнефть"]],
     "addr_patterns": [["294"], ["малые бикшихи"], ["канашский муниципальный округ"]]},
    {"id": "tatneft_68", "x": 497, "y": 762, "name": "Татнефть №68", "label_pos": "left",
     "name_patterns": [["татнефть"]], "addr_patterns": [["46-й километр"]],
     # у №68 источники отдают только общий адрес без улицы/дома
     "addr_exact": ["азс", "чувашская республика"]},
]

default_fuels = ("АИ-92", "АИ-95", "ДТ", "Газ", "АИ-98")


def _contains_all(text, subs):
    text = (text or "").lower()
    return all(sub.lower() in text for sub in subs)


def match_point(station, points):
    # возвращает описание точки карты для станции, или None.
    name = station.get("name") or ""
    address = station.get("address") or ""
    for pt in points:
        name_ok = any(_contains_all(name, pat) for pat in pt["name_patterns"])
        addr_ok = any(_contains_all(address, pat) for pat in pt["addr_patterns"])
        if not addr_ok:
            addr_ok = address.strip().lower() in pt.get("addr_exact", ())
        if name_ok and addr_ok:
            return pt
    return None


def summary_status(fuels, selected_fuels=None):
    # сводный статус азс по выбранным видам топлива (лучший).
    names = selected_fuels if selected_fuels is not None else list(fuels)
    best = "unknown"
    for name in names:
        status = fuels.get(name, "unknown")
        if status not in STATUS_ORDER:
            status = "unknown"
        if STATUS_ORDER.index(status) < STATUS_ORDER.index(best):
            best = status
    return best


def status_color(fuels, selected_fuels=None):
    # цвет кружка по тем же видам топлива, что показаны в плашке
    return COLORS[STATUS_ORDER.index(summary_status(fuels, selected_fuels))]


def fuel_text(status):
    return fuel_labels.get(status, "Неизвестно")


def generate_map(input_path="map_clean.png", output_path="map_out.png",
                 stations_data=None, selected_fuels=None):
    base_img = Image.open(input_path).convert("RGBA")
    w, h = base_img.size

    s = 4
    overlay = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    k = 1.2
    outer_r = int(11 * k * s)   # Серая граница
    color_r = int(9 * k * s)    # Основной цвет
    inner_r = int(4 * k * s)    # Белый центр

    stations_data = stations_data or []
    selected_fuels = selected_fuels or default_fuels

    # ставим станции с точками карты
    point_station = {}
    for station in stations_data:
        pt = match_point(station, stations)
        if pt is not None and pt["id"] not in point_station:
            point_station[pt["id"]] = station

    # шрифты
    try:
        font_name = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20 * s)
        font_fuel = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16 * s)
    except OSError:
        try:
            font_name = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20 * s)
            font_fuel = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16 * s)
        except OSError:
            font_name = ImageFont.load_default()
            font_fuel = ImageFont.load_default()

    # отступ плашки от края кружка (уже с учетом k = 1.2)
    label_gap = outer_r + 10 * s

    # рисуем точки на карте — по умолчанию серые, окрашиваются только станции из источника
    for pt in stations:
        cx, cy = pt["x"] * s, pt["y"] * s
        station = point_station.get(pt["id"])

        if station is not None:
            fill_color = status_color(station.get("fuels", {}), selected_fuels)
        else:
            fill_color = gray_color

        draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r), fill=border_gray)
        draw.ellipse((cx - color_r, cy - color_r, cx + color_r, cy + color_r), fill=fill_color)
        draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), fill=inner_white)

    # плашки с названием и наличием топлива
    # размеры плашек и желаемое положение (с индивидуальными смещениями)
    plates = []
    for pt in stations:
        station = point_station.get(pt["id"])
        x, y = pt["x"] * s, pt["y"] * s
        pos = pt["label_pos"]

        lines = [pt["name"]]
        fuels_now = station.get("fuels", {}) if station is not None else {}
        for fuel in selected_fuels:
            lines.append(f"{fuel}: {fuel_text(fuels_now.get(fuel, 'unknown'))}")

        line_bboxes = [
            draw.textbbox((0, 0), line, font=font_name if i == 0 else font_fuel)
            for i, line in enumerate(lines)
        ]
        max_w = max((b[2] - b[0]) for b in line_bboxes)
        total_h = sum((b[3] - b[1]) for b in line_bboxes) + (len(lines) - 1) * 6 * s

        padding = 10 * s
        box_w = max_w + padding * 2
        box_h = total_h + padding * 2

        if pos == "left":
            bx = x - box_w - label_gap
            by = y - box_h // 2
        elif pos == "right":
            bx = x + label_gap
            by = y - box_h // 2
        elif pos == "bottom":
            bx = x - box_w // 2
            by = y + label_gap
        elif pos == "bottom_left":
            bx = x - box_w - label_gap
            by = y + label_gap
        elif pos == "top_right":
            bx = x + label_gap
            by = y - box_h - label_gap
        else:
            bx = x - box_w // 2
            by = y - box_h - label_gap

        # --- Индивидуальные смещения ---
        if pt["id"] == "bashneft":
            by -= int(box_h * 0.2)
        elif pt["id"] == "tatneft_66":
            by += int(box_h * 0.05)
            bx += int(box_w * 0.05)
        elif pt["id"] == "tatneft_68":
            bx -= int(box_w * 0.15)
        elif pt["id"] == "lukoil":
            bx += 4 * s
        elif pt["id"] == "quickstop":
            bx += 14 * s
            by += 6 * s
        elif pt["id"] == "tat_ekonom":
            by -= 4 * s

        plates.append({
            "pt": pt, "lines": lines, "padding": padding, "cx": x, "cy": y,
            "w": box_w, "h": box_h,
            "x": max(0, min(bx, w * s - box_w)),
            "y": max(0, min(by, h * s - box_h)),
        })

    # раздвигаем плашки, чтобы они не пересекались друг с другом,
    #     с кружками и с легендой. Двигаются только те, что мешают друг другу.
    leg_w, leg_h = 265 * s, 175 * s
    lx = (w - 265 - 20) * s
    ly = (h - 175 - 36) * s
    legend_rect = (lx, ly, lx + leg_w, ly + leg_h)

    plate_margin = 8 * s                 # минимальный зазор между плашками
    circle_margin = outer_r + 4 * s      # плашка не заезжает на кружки
    step = 4 * s
    max_dist = label_gap * 4             # дальше от своего кружка не уводим

    def rect_overlap(a, b, margin=0):
        ow = min(a[2], b[2] + margin) - max(a[0], b[0] - margin)
        oh = min(a[3], b[3] + margin) - max(a[1], b[1] - margin)
        return ow * oh if ow > 0 and oh > 0 else 0

    def dist_to_rect(px, py, r):
        dx = max(r[0] - px, 0, px - r[2])
        dy = max(r[1] - py, 0, py - r[3])
        return (dx * dx + dy * dy) ** 0.5

    def penalty(idx, rect):
        total = 0
        for k, other in enumerate(plates):
            if k != idx:
                other_rect = (other["x"], other["y"], other["x"] + other["w"], other["y"] + other["h"])
                total += rect_overlap(rect, other_rect, plate_margin)
        total += rect_overlap(rect, legend_rect, plate_margin)
        for p2 in stations:
            if dist_to_rect(p2["x"] * s, p2["y"] * s, rect) < circle_margin:
                total += 10 ** 7
        return total

    def current_rect(item):
        return (item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"])

    for _ in range(4):
        moved = False
        for idx, item in enumerate(plates):
            if penalty(idx, current_rect(item)) == 0:
                continue

            reach_x = item["w"] + max_dist
            reach_y = item["h"] + max_dist
            candidates = []
            for dy in range(-reach_y, reach_y + 1, step):
                for dx in range(-reach_x, reach_x + 1, step):
                    nx, ny = item["x"] + dx, item["y"] + dy
                    if nx < 0 or ny < 0 or nx + item["w"] > w * s or ny + item["h"] > h * s:
                        continue
                    rect = (nx, ny, nx + item["w"], ny + item["h"])
                    if dist_to_rect(item["cx"], item["cy"], rect) > max_dist:
                        continue
                    candidates.append((dx * dx + dy * dy, nx, ny))
            candidates.sort()

            best = None
            for _, nx, ny in candidates:
                rect = (nx, ny, nx + item["w"], ny + item["h"])
                value = penalty(idx, rect)
                if value == 0:
                    best = (nx, ny)
                    break
                if best is None or value < best[2]:
                    best = (nx, ny, value)

            if best is not None and (best[0], best[1]) != (item["x"], item["y"]):
                item["x"], item["y"] = best[0], best[1]
                moved = True
        if not moved:
            break

    # рисуем сначала линии от каждого кружка к его плашке, затем плашки
    for item in plates:
        rect = current_rect(item)
        tx = min(max(item["cx"], rect[0]), rect[2])
        ty = min(max(item["cy"], rect[1]), rect[3])
        draw.line((item["cx"], item["cy"], tx, ty), fill=border_gray, width=2 * s)

    # кружки поверх линий
    for pt in stations:
        cx, cy = pt["x"] * s, pt["y"] * s
        station = point_station.get(pt["id"])
        fill_color = status_color(station.get("fuels", {}), selected_fuels) if station is not None else gray_color
        draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r), fill=border_gray)
        draw.ellipse((cx - color_r, cy - color_r, cx + color_r, cy + color_r), fill=fill_color)
        draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), fill=inner_white)

    for item in plates:
        bx, by, padding = item["x"], item["y"], item["padding"]
        draw.rounded_rectangle(
            (bx, by, bx + item["w"], by + item["h"]),
            radius=8 * s,
            fill=(255, 255, 255, 230),
            outline=(180, 180, 180, 255),
            width=2 * s,
        )

        ty = by + padding
        for i, line in enumerate(item["lines"]):
            f = font_name if i == 0 else font_fuel
            draw.text((bx + padding, ty), line, fill="#222222", font=f)
            tb = draw.textbbox((0, 0), line, font=f)
            ty += (tb[3] - tb[1]) + 6 * s

    # легенда в правом нижнем углу
    leg_w, leg_h = 265 * s, 175 * s
    lx = (w - 265 - 20) * s
    ly = (h - 175 - 36) * s

    draw.rounded_rectangle(
        (lx, ly, lx + leg_w, ly + leg_h),
        radius=12 * s,
        fill=(255, 255, 255, 235),
        outline=(180, 180, 180, 255),
        width=int(1.5 * s)
    )

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18 * s)
    except OSError:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18 * s)

    l_outer = int(10.5 * s)
    l_color = int(8.5 * s)
    l_inner = int(3.8 * s)

    for idx, (col, text) in enumerate(oil_status):
        cx = lx + 28 * s
        cy = ly + (32 + idx * 36) * s
        draw.ellipse((cx - l_outer, cy - l_outer, cx + l_outer, cy + l_outer), fill=border_gray)
        draw.ellipse((cx - l_color, cy - l_color, cx + l_color, cy + l_color), fill=col)
        draw.ellipse((cx - l_inner, cy - l_inner, cx + l_inner, cy + l_inner), fill=inner_white)
        draw.text((cx + 22 * s, cy - 10 * s), text, fill="#222222", font=font)

    overlay_smooth = overlay.resize((w, h), resample=Image.Resampling.LANCZOS)
    final_img = Image.alpha_composite(base_img, overlay_smooth)
    final_img.save(output_path)

    return len(point_station), len(stations)


if __name__ == "__main__":
    generate_map()
