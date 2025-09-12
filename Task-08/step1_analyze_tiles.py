import os
import re
import csv
import cv2
import numpy as np

ASSETS_DIR = "assets"
OUT_DIR = "debug_overlays"
RESULTS_CSV = "tile_results.csv"

STD_THRESH = 6
BRIGHT_THRESH = 245
MIN_CONTOUR_AREA = 50

os.makedirs(OUT_DIR, exist_ok=True)

def sorted_asset_paths(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    def keyfn(name):
        m = re.match(r"^(\d+)", name)
        return int(m.group(1)) if m else 10**9
    files.sort(key=keyfn)
    return [os.path.join(folder, f) for f in files]

def analyze_tile(path):
    fname = os.path.basename(path)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return {"filename": fname, "error": "load_failed"}

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_gray = float(np.mean(gray))
    std_gray = float(np.std(gray))

    if std_gray < STD_THRESH or mean_gray > BRIGHT_THRESH:
        mean_bgr = cv2.mean(img)[:3]
        mean_rgb = (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))

        overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.putText(overlay, "BLANK", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        out_name = os.path.join(OUT_DIR, f"ov_{fname}")
        cv2.imwrite(out_name, overlay)
        return {
            "filename": fname,
            "blank": True,
            "cx": None,
            "cy": None,
            "r": mean_rgb[0],
            "g": mean_rgb[1],
            "b": mean_rgb[2],
            "area": 0,
            "mean_gray": mean_gray,
            "std_gray": std_gray
        }

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    white_frac = np.mean(th == 255)
    if white_frac > 0.5:
        th = cv2.bitwise_not(th)

    kernel = np.ones((3, 3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:

        mean_bgr = cv2.mean(img)[:3]
        mean_rgb = (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))
        overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.putText(overlay, "NO_CONTOUR", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite(os.path.join(OUT_DIR, f"ov_{fname}"), overlay)
        return {
            "filename": fname,
            "blank": True,
            "cx": None,
            "cy": None,
            "r": mean_rgb[0],
            "g": mean_rgb[1],
            "b": mean_rgb[2],
            "area": 0,
            "mean_gray": mean_gray,
            "std_gray": std_gray
        }

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < MIN_CONTOUR_AREA:
        mean_bgr = cv2.mean(img)[:3]
        mean_rgb = (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))
        overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.putText(overlay, "SMALL_CONTOUR", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite(os.path.join(OUT_DIR, f"ov_{fname}"), overlay)
        return {
            "filename": fname,
            "blank": True,
            "cx": None,
            "cy": None,
            "r": mean_rgb[0],
            "g": mean_rgb[1],
            "b": mean_rgb[2],
            "area": area,
            "mean_gray": mean_gray,
            "std_gray": std_gray
        }

    M = cv2.moments(largest)
    if M["m00"] == 0:
        cx, cy = w // 2, h // 2
    else:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [largest], -1, 255, -1)
    mean_bgr = cv2.mean(img, mask=mask)[:3]
    mean_rgb = (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))

    overlay = img.copy()
    cv2.drawContours(overlay, [largest], -1, (0, 255, 0), 2)
    cv2.circle(overlay, (cx, cy), 4, (0, 0, 255), -1)
    text = f"{fname}  center=({cx},{cy})  color={mean_rgb}"
    cv2.putText(overlay, text, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1, cv2.LINE_AA)
    out_name = os.path.join(OUT_DIR, f"ov_{fname}")
    cv2.imwrite(out_name, overlay)

    return {
        "filename": fname,
        "blank": False,
        "cx": cx,
        "cy": cy,
        "r": mean_rgb[0],
        "g": mean_rgb[1],
        "b": mean_rgb[2],
        "area": area,
        "mean_gray": mean_gray,
        "std_gray": std_gray
    }

def main():
    paths = sorted_asset_paths(ASSETS_DIR)
    if not paths:
        print("No images found in", ASSETS_DIR)
        return

    results = []
    for i, p in enumerate(paths):
        print(f"[{i+1}/{len(paths)}] Processing {os.path.basename(p)}")
        res = analyze_tile(p)
        results.append(res)

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "blank", "cx", "cy", "r", "g", "b", "area", "mean_gray", "std_gray", "error"])
        for r in results:
            writer.writerow([
                r.get("filename"),
                r.get("blank"),
                r.get("cx"),
                r.get("cy"),
                r.get("r"),
                r.get("g"),
                r.get("b"),
                r.get("area"),
                r.get("mean_gray"),
                r.get("std_gray"),
                r.get("error", "")
            ])
    print("Saved results to", RESULTS_CSV)
    print("Saved overlays to", OUT_DIR)

if __name__ == "__main__":
    main()
