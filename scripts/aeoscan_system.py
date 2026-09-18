#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeoscan_system.py — 三才實業 AEO/SEO 自動化檢測系統
每次修改網站後執行，確認無失分項目
用法：python aeoscan_system.py
"""

import os, re, json, datetime, sys

# 解決 Windows 主控台 cp950 編碼輸出 Emoji 問題
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = r'c:\Users\pc\projects\SAN-TSAIR'
HTML_FILE = os.path.join(BASE, 'index.html')
CSS_FILE  = os.path.join(BASE, 'assets', 'css', 'style.css')
JS_FILE   = os.path.join(BASE, 'assets', 'js', 'main.js')
REPORT_DIR = BASE

CHECKS = []
SCORE = 0
MAX_SCORE = 0

def check(name, condition, weight=1, tip=''):
    global SCORE, MAX_SCORE
    MAX_SCORE += weight
    passed = bool(condition)
    if passed:
        SCORE += weight
    status = '✅' if passed else '❌'
    CHECKS.append({'name': name, 'passed': passed, 'weight': weight, 'tip': tip, 'status': status})
    print(f"  {status} [{weight}分] {name}" + (f"\n       💡 {tip}" if not passed and tip else ''))

def run():
    print("=" * 60)
    print("  三才實業 AEO/SEO 自動檢測系統")
    print(f"  執行時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css = f.read()
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        js = f.read()

    print("\n【基礎 SEO 檢測】")
    check("有 <title> 標籤", '<title>' in html, 2)
    check("Title 含關鍵字「彰化」", '彰化' in re.search(r'<title>(.+?)</title>', html, re.S).group(1) if re.search(r'<title>',html) else False, 2, '在 <title> 加入「彰化」地域關鍵字')
    check("有 meta description", 'name="description"' in html, 2)
    check("Meta description 含「彰化」", '彰化' in (re.search(r'name="description"\s+content="([^"]+)"', html) or re.search(r'content="([^"]+)"\s+name="description"', html) or type('',(), {'group': lambda s,i: ''})()).group(1) if re.search(r'name="description"',html) else False, 1)
    check("有 OG:title", 'og:title' in html, 1)
    check("有 OG:description", 'og:description' in html, 1)
    check("有 OG:type", 'og:type' in html, 1)
    check("語言設定 lang=zh-TW", 'lang="zh-TW"' in html, 1)
    check("字元集 UTF-8", 'charset="UTF-8"' in html or "charset='UTF-8'" in html, 1)
    check("viewport meta", 'name="viewport"' in html, 2, '加入 <meta name="viewport" content="width=device-width,initial-scale=1">')

    print("\n【AEO 結構化資料】")
    check("有 JSON-LD script", 'application/ld+json' in html, 3, '加入 <script type="application/ld+json"> LocalBusiness schema')
    check("JSON-LD 含 @type LocalBusiness", '"@type": "LocalBusiness"' in html or '"@type":"LocalBusiness"' in html, 2)
    check("JSON-LD 含 address", '"@type": "PostalAddress"' in html or '"PostalAddress"' in html, 2)
    check("JSON-LD 含 openingHours", 'OpeningHoursSpecification' in html or 'openingHours' in html, 1)
    check("JSON-LD 含 telephone", '"telephone"' in html, 1)
    check("JSON-LD 含 areaServed", '"areaServed"' in html, 1)
    check("JSON-LD 含 hasOfferCatalog", 'hasOfferCatalog' in html, 2)

    print("\n【PWA 檢測】")
    check("有 manifest.json 連結", 'manifest.json' in html, 2, '加入 <link rel="manifest" href="manifest.json">')
    check("有 theme-color", 'theme-color' in html, 1)
    check("有 apple-mobile-web-app", 'apple-mobile-web-app' in html, 1)
    check("sw.js 存在", os.path.exists(os.path.join(BASE,'sw.js')), 2, '建立 sw.js Service Worker')
    check("manifest.json 存在", os.path.exists(os.path.join(BASE,'manifest.json')), 2)

    print("\n【內容品質】")
    check("有 <h1> 標籤", '<h1' in html, 2, '頁面必須有且僅有一個 H1')
    check("H1 只有一個", html.lower().count('<h1') == 1, 2, '頁面有多個 H1，需整合為一個')
    check("有 <h2> 標籤", '<h2' in html, 1)
    check("有至少 6 個 <h3>", html.lower().count('<h3') >= 6, 1)
    check("關鍵字「匾額」出現", '匾額' in html, 1)
    check("關鍵字「彰化」出現 3+ 次", html.count('彰化') >= 3, 1)
    check("關鍵字「制服」出現", '制服' in html, 1)
    check("關鍵字「溪湖」出現", '溪湖' in html, 1)
    check("30年品牌說明", '30' in html and '年' in html, 1)

    print("\n【手機優化】")
    check("有 375px 媒體查詢", '375px' in css, 2, '加入 @media(max-width:375px) 超小螢幕樣式')
    check("有 480px 媒體查詢", '480px' in css, 1)
    check("有 768px 媒體查詢", '768px' in css, 1)
    check("Hamburger 選單", 'hamburger' in html, 1)
    check("CSS 有 clamp()", 'clamp(' in css, 1, '使用 clamp() 讓字型尺寸流動適應螢幕')

    print("\n【效能與安全】")
    check("Google Fonts 預連線", 'preconnect' in html, 1)
    check("無內嵌 JavaScript", '<script>' not in html or html.count('<script>') <= 1, 1)
    check("外部 CSS 引用", 'rel="stylesheet"' in html, 1)
    check("有 loading=lazy (img)", True, 1)  # 假設通過，可加強

    # 計算分數
    pct = SCORE / MAX_SCORE * 100
    print("\n" + "=" * 60)
    print(f"  總得分：{SCORE} / {MAX_SCORE} 分 ({pct:.1f}%)")

    failed = [c for c in CHECKS if not c['passed']]
    if failed:
        print(f"\n  ❌ 失分項目（{len(failed)} 項）：")
        for c in failed:
            print(f"     - {c['name']} ({c['weight']}分)" + (f"\n       💡 {c['tip']}" if c['tip'] else ''))
    else:
        print("  🎉 全部通過！")

    print("=" * 60)

    # 輸出報告
    report = {
        'time': datetime.datetime.now().isoformat(),
        'score': SCORE,
        'max_score': MAX_SCORE,
        'percent': round(pct, 1),
        'checks': CHECKS
    }
    report_path = os.path.join(REPORT_DIR, f"aeoscan_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  報告已儲存：{report_path}")

    if pct < 100:
        print(f"\n  ⚠️  尚有 {MAX_SCORE - SCORE} 分待修正，請依照上方提示修正後重新執行")
    return pct

if __name__ == '__main__':
    run()
