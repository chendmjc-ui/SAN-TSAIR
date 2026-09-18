"""
把體積過大的廠商型錄 PDF（P:\@三才WEB 底下，單檔 12-39MB）拆頁、縮放、轉 webp，
輸出到 assets/images/catalog/<vendor>/<catalog>/page-NN.webp，供網站用圖片瀏覽器顯示，
不把原始 PDF 放進 git repo。

參數依實測結果：寬度 1100px、webp quality 72 —— 落在業界建議的網頁 PDF 縮減區間上限（-80%），
肉眼比對文字/色彩無明顯損失。見 docs/apps_script_form_setup.md 同批交接紀錄。
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_BASE = os.path.join(ROOT, 'assets', 'images', 'catalog')
WIDTH = 1100
QUALITY = 72

SOURCE = r'P:\@三才WEB\1-廠商同意三才使用資料\制服'

JOBS = [
    ('fulaike', [
        ('diaox-no3', 'Diaox No.3.pdf'),
        ('no17-uk', 'no.17 U.K.pdf'),
        ('no33-baida', 'no.33 百達 秋冬.pdf'),
    ]),
    ('weiwei', [
        ('2025-fw', '2025秋冬.pdf'),
        ('2026-ss', '2026春夏(雙頁).pdf'),
    ]),
    ('wanyu', [
        ('2026-summer-1', '萬宇2026夏季-PDF檔~1.pdf'),
        ('2026-summer-2', '萬宇2026~夏季~PDF檔-2.pdf'),
    ]),
]


def extract(pdf_path, out_dir):
    # 直接把整頁「渲染」成點陣圖（而非抽取內嵌圖片物件），
    # 避免個別頁面用到 PDF 罕見編碼（如 JPEG2000）時 PIL 解不開而整支腳本中斷
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    total_bytes = 0
    for i in range(doc.page_count):
        page = doc[i]
        zoom = WIDTH / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        out_path = os.path.join(out_dir, f'page-{count+1:02d}.webp')
        img.save(out_path, 'webp', quality=QUALITY)
        total_bytes += os.path.getsize(out_path)
        count += 1
    doc.close()
    return count, total_bytes


def main():
    grand_total = 0
    for vendor, catalogs in JOBS:
        for slug, filename in catalogs:
            pdf_path = os.path.join(SOURCE, vendor_dirname(vendor), filename)
            out_dir = os.path.join(OUT_BASE, vendor, slug)
            pages, size = extract(pdf_path, out_dir)
            grand_total += size
            print(f'{vendor}/{slug}: {pages} 頁, {size/1024/1024:.2f} MB')
    print(f'總計: {grand_total/1024/1024:.2f} MB')


def vendor_dirname(vendor):
    return {
        'fulaike': '富雷克',
        'weiwei': '瑋瑋服飾',
        'wanyu': '萬宇',
    }[vendor]


if __name__ == '__main__':
    main()
