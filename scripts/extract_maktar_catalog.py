"""
把 Maktar Qubii Duo 的型錄 PDF 拆頁、縮放、轉 webp，
輸出到 assets/images/catalog/maktar/<catalog>/page-NN.webp，供網站用圖片瀏覽器顯示，
不把原始 PDF 放進 git repo。參數與 extract_catalog_pdfs.py 一致（寬度 1100px、webp quality 72）。
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_BASE = os.path.join(ROOT, 'assets', 'images', 'catalog', 'maktar')
WIDTH = 1100
QUALITY = 72

SOURCE = r'P:\@三才WEB\2-廠商要先看三才網頁才決定是否能使用資料\同意-但要先看三才網站\Maktar--Qubii Duo手機自動備份'

JOBS = [
    ('catalog', 'Maktar企業產品型錄.pdf'),
    ('sales-kit', 'Qubii Duo Sales kit.pdf'),
]


def extract(pdf_path, out_dir):
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
    for slug, filename in JOBS:
        pdf_path = os.path.join(SOURCE, filename)
        out_dir = os.path.join(OUT_BASE, slug)
        pages, size = extract(pdf_path, out_dir)
        grand_total += size
        print(f'maktar/{slug}: {pages} 頁, {size/1024/1024:.2f} MB')
    print(f'總計: {grand_total/1024/1024:.2f} MB')


if __name__ == '__main__':
    main()
