import os
import csv
import math
from PIL import Image, ImageDraw
import cv2
import numpy as np

ASSETS_DIR = "assets"
CSV_FILE = "tile_results.csv"
OUTPUT_FILE = "treasure_map.png"

TILE = 128
MARGIN = 40
POINT_RADIUS = 8
LINE_WIDTH = 4
MAX_COLS = 20
ROW_SPACING = 20

def read_results_csv(csv_path):
    results = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row.get("filename") or row.get("file") or ""
            blank = str(row.get("blank","")).strip().lower() in ("true","1","yes")
            cx = int(row["cx"]) if row.get("cx") not in (None,"","None") else None
            cy = int(row["cy"]) if row.get("cy") not in (None,"","None") else None
            try:
                r = int(row["r"]) if row.get("r") not in (None,"","") else 200
                g = int(row["g"]) if row.get("g") not in (None,"","") else 200
                b = int(row["b"]) if row.get("b") not in (None,"","") else 200
            except:
                r,g,b = 200,200,200
            results.append({"filename": fname, "blank": blank, "cx": cx, "cy": cy, "color": (r,g,b)})
    return results

def analyze_tile_quick(path):

    img = cv2.imread(path)
    h,w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if np.std(gray) < 6 or np.mean(gray) > 245:
        mean_bgr = cv2.mean(img)[:3]
        return {"filename": os.path.basename(path), "blank": True, "cx": None, "cy": None, "color": (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))}
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(th==255) > 0.5:
        th = cv2.bitwise_not(th)
    kernel = np.ones((3,3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        mean_bgr = cv2.mean(img)[:3]
        return {"filename": os.path.basename(path), "blank": True, "cx": None, "cy": None, "color": (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))}
    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        cx,cy = w//2, h//2
    else:
        cx = int(M["m10"]/M["m00"]); cy = int(M["m01"]/M["m00"])
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [largest], -1, 255, -1)
    mean_bgr = cv2.mean(img, mask=mask)[:3]
    return {"filename": os.path.basename(path), "blank": False, "cx": cx, "cy": cy, "color": (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))}

def gather_tile_data():

    if os.path.exists(CSV_FILE):
        print("Reading tile data from", CSV_FILE)
        rows = read_results_csv(CSV_FILE)
        if rows:
            return rows

    print("CSV not found or empty — analyzing assets directly")
    files = sorted([f for f in os.listdir(ASSETS_DIR) if f.lower().endswith((".png",".jpg",".jpeg"))])
    results = []
    for f in files:
        path = os.path.join(ASSETS_DIR, f)
        print("Analyzing", f)
        results.append(analyze_tile_quick(path))
    return results

def compute_layout(n):
    cols = min(n, MAX_COLS)
    rows = math.ceil(n / cols)
    canvas_w = MARGIN*2 + cols * TILE
    canvas_h = MARGIN*2 + rows * TILE + (rows-1) * ROW_SPACING
    return cols, rows, canvas_w, canvas_h

def draw_map(tile_data):
    n = len(tile_data)
    cols, rows, W, H = compute_layout(n)
    im = Image.new("RGB", (W, H), (255,255,255))
    draw = ImageDraw.Draw(im)

    positions = []
    for i, t in enumerate(tile_data):
        col = i % cols
        row = i // cols
        base_x = MARGIN + col * TILE
        base_y = MARGIN + row * (TILE + ROW_SPACING)
        if t["blank"] or t["cx"] is None:
            gx = base_x + TILE//2
            gy = base_y + TILE//2
            positions.append({"pos": (gx, gy), "blank": True, "color": t["color"], "name": t["filename"]})
        else:
            gx = base_x + t["cx"]
            gy = base_y + t["cy"]
            positions.append({"pos": (gx, gy), "blank": False, "color": t["color"], "name": t["filename"]})

    last_valid = None
    for i, p in enumerate(positions):
        gx, gy = p["pos"]
        if p["blank"]:
            r = POINT_RADIUS
            draw.ellipse((gx-r, gy-r, gx+r, gy+r), outline=(120,120,120), width=2)
            draw.line((gx-r, gy-r, gx+r, gy+r), fill=(120,120,120), width=2)
            draw.line((gx-r, gy+r, gx+r, gy-r), fill=(120,120,120), width=2)
            last_valid = None
            continue
        color = tuple(p["color"])
        draw.ellipse((gx-POINT_RADIUS, gy-POINT_RADIUS, gx+POINT_RADIUS, gy+POINT_RADIUS), fill=color, outline=(0,0,0))
        if last_valid is not None:
            sx, sy = last_valid["pos"]
            line_color = tuple(last_valid["color"])
            draw.line((sx, sy, gx, gy), fill=line_color, width=LINE_WIDTH)
        last_valid = p

    im.save(OUTPUT_FILE)
    print("Saved final treasure map to", OUTPUT_FILE)

if __name__ == "__main__":
    tile_data = gather_tile_data()
    if not tile_data:
        print("No tiles found. Check", ASSETS_DIR)
    else:
        draw_map(tile_data)
