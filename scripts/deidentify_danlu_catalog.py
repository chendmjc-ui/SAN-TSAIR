"""
丹露實業型錄圖片去識別化：用 rapidocr 抓出售價/箱入數文字座標，
篩選後用背景色中位數色塊塗銷。用法：
  py -3 scripts/deidentify_danlu_catalog.py extract   # 只跑OCR、印出所有文字框，供人工複核篩選規則
  py -3 scripts/deidentify_danlu_catalog.py redact     # 依篩選規則實際塗銷並輸出結果
"""
import sys
import io
import re
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from rapidocr_onnxruntime import RapidOCR

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC_DIR = Path(r"C:\Users\pc\AppData\Local\Temp\danlu_review")
OUT_DIR = SRC_DIR / "redacted"
OUT_DIR.mkdir(exist_ok=True)
FILES = ["oichan.webp", "danro.webp", "hapado.webp", "kukkar.webp"]

PRICE_RE = re.compile(r"售\s*價")
YUAN_RE = re.compile(r"[\d,，]+\s*元")
QTY_RE = re.compile(r"\d+\s*(只|組|入|套|个|個)\s*/?\s*箱")

engine = RapidOCR()

# rapidocr 這兩處這批圖沒偵測到（信心度太低被跳過或漏檢），人工複查後補上
# 座標是在原圖（oichan.webp/hapado.webp）上用網格裁圖手動核對過的精確值
MANUAL_EXTRA = {
    "oichan.webp": [(1105, 1598, 1213, 1624, "qty")],   # OIC-071114 「20組/箱」
    "hapado.webp": [(786, 690, 858, 716, "qty")],        # HAP-3P 「36組/箱」
}

def run_ocr(path):
    img = np.array(Image.open(path).convert("RGB"))
    result, _ = engine(img)
    boxes = []
    if result:
        for poly, text, conf in result:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            boxes.append({
                "text": text,
                "conf": float(conf),
                "x0": min(xs), "y0": min(ys), "x1": max(xs), "y1": max(ys),
            })
    return boxes

def find_spans(text):
    """回傳這段文字裡所有需要塗銷的字元範圍 (start,end,kind)，
    用來處理『商品名稱+售價/箱入數』被 OCR 併成同一個框的情況——
    不能整框塗銷（會連商品名稱一起蓋掉），要用字元位置比例換算出只蓋
    價格/箱入數那一小段的子區間。"""
    spans = []
    price_start = None
    m = PRICE_RE.search(text)
    if m:
        price_start = m.start()
    m2 = YUAN_RE.search(text)
    if m2:
        start = price_start if price_start is not None else m2.start()
        spans.append((start, m2.end(), "price"))
    m3 = QTY_RE.search(text)
    if m3:
        spans.append((m3.start(), m3.end(), "qty"))
    return spans

def classify(text):
    has_price = bool(PRICE_RE.search(text) or YUAN_RE.search(text))
    has_qty = bool(QTY_RE.search(text))
    return has_price, has_qty

def _char_w(ch):
    # 半形數字/逗號/斜線比全形中日文字窄很多，線性等寬估計會系統性偏移，
    # 用權重修正，不然「組」這種字常被切到一半
    if ch.isascii():
        return 0.55
    return 1.0

def sub_box(b, start, end):
    text = b["text"]
    weights = [_char_w(c) for c in text]
    total = sum(weights) or 1.0
    before = sum(weights[:start])
    upto_end = sum(weights[:end])
    w = b["x1"] - b["x0"]
    fx0 = b["x0"] + (before / total) * w
    fx1 = b["x0"] + (upto_end / total) * w
    return fx0, b["y0"], fx1, b["y1"]

def refine_split_x(gray, x_est, y0, y1, x_min, x_max, search=35):
    """字元寬度用比例估的分界點常常差個10幾px，切到字的一半。
    在估計點附近找『墨色最淡的一整欄』當作真正的字間空隙，比死算比例準。"""
    lo = max(int(x_est - search), x_min)
    hi = min(int(x_est + search), x_max)
    if hi <= lo:
        return x_est
    y0i, y1i = int(y0), int(y1)
    col_std = gray[y0i:y1i, lo:hi].astype(np.float32).std(axis=0)
    if col_std.size == 0:
        return x_est
    # 找最淡的窗口（寬度~4px滑動平均），避免抓到單一雜訊像素
    k = 4
    if col_std.size >= k:
        kernel = np.ones(k) / k
        smoothed = np.convolve(col_std, kernel, mode="valid")
        best = int(np.argmin(smoothed)) + k // 2
    else:
        best = int(np.argmin(col_std))
    return lo + best

def extract_mode():
    for fname in FILES:
        path = SRC_DIR / fname
        boxes = run_ocr(path)
        print(f"\n===== {fname} ({len(boxes)} boxes) =====")
        for b in boxes:
            spans = find_spans(b["text"])
            for start, end, kind in spans:
                fx0, fy0, fx1, fy1 = sub_box(b, start, end)
                whole = "WHOLE" if (start == 0 and end == len(b["text"])) else "PARTIAL"
                print(f"[{kind}|{whole}] subbox=({fx0:.0f},{fy0:.0f},{fx1:.0f},{fy1:.0f}) "
                      f"fullbox=({b['x0']:.0f},{b['y0']:.0f},{b['x1']:.0f},{b['y1']:.0f}) "
                      f"conf={b['conf']:.2f} text={b['text']!r}")
        out_json = SRC_DIR / f"{fname}.ocr.json"
        out_json.write_text(json.dumps(boxes, ensure_ascii=False, indent=2), encoding="utf-8")

def redact_box(im_arr, draw, x0, y0, x1, y1, pad=4):
    W, H = im_arr.shape[1], im_arr.shape[0]
    ex0, ey0 = max(int(x0 - pad), 0), max(int(y0 - pad), 0)
    ex1, ey1 = min(int(x1 + pad), W), min(int(y1 + pad), H)
    edge = []
    edge.append(im_arr[ey0:ey0+2, ex0:ex1].reshape(-1, 3))
    edge.append(im_arr[max(ey1-2,ey0):ey1, ex0:ex1].reshape(-1, 3))
    edge.append(im_arr[ey0:ey1, ex0:ex0+2].reshape(-1, 3))
    edge.append(im_arr[ey0:ey1, max(ex1-2,ex0):ex1].reshape(-1, 3))
    px = np.concatenate([e for e in edge if e.size], axis=0)
    color = tuple(int(v) for v in np.median(px, axis=0))
    draw.rectangle([ex0, ey0, ex1, ey1], fill=color)
    return (ex0, ey0, ex1, ey1)

def redact_mode():
    manifest = {}
    for fname in FILES:
        path = SRC_DIR / fname
        boxes = run_ocr(path)
        im = Image.open(path).convert("RGB")
        arr = np.array(im)
        gray = np.array(im.convert("L"))
        draw = ImageDraw.Draw(im)
        redacted_boxes = []
        for b in boxes:
            spans = find_spans(b["text"])
            for start, end, kind in spans:
                fx0, fy0, fx1, fy1 = sub_box(b, start, end)
                if start > 0:
                    fx0 = refine_split_x(gray, fx0, fy0, fy1, b["x0"], b["x1"])
                if end < len(b["text"]):
                    fx1 = refine_split_x(gray, fx1, fy0, fy1, b["x0"], b["x1"])
                box = redact_box(arr, draw, fx0, fy0, fx1, fy1)
                redacted_boxes.append({"box": box, "text": b["text"], "kind": kind})
        for (mx0, my0, mx1, my1, kind) in MANUAL_EXTRA.get(fname, []):
            box = redact_box(arr, draw, mx0, my0, mx1, my1, pad=0)
            redacted_boxes.append({"box": box, "text": "(manual)", "kind": kind})
        out_path = OUT_DIR / fname.replace(".webp", ".png")
        im.save(out_path)
        manifest[fname] = redacted_boxes
        print(f"{fname}: {len(redacted_boxes)} boxes redacted -> {out_path}")
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if mode == "extract":
        extract_mode()
    elif mode == "redact":
        redact_mode()
    else:
        print("用法: extract | redact")
