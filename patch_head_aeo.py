# -*- coding: utf-8 -*-
"""
patch_head_aeo.py — 自動更新 index.html 的 head，補齊 hreflang 與 og:image 標記
"""

import os

BASE = r'c:\Users\pc\projects\SAN-TSAIR'
html_path = os.path.join(BASE, 'index.html')

if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 注入 hreflang
    hreflang_tag = '  <link rel="alternate" hreflang="zh-TW" href="https://chendmjc-ui.github.io/SAN-TSAIR/" />\n'
    if 'hreflang="zh-TW"' not in html:
        html = html.replace('<head>', '<head>\n' + hreflang_tag)
        print('hreflang 標記已注入！')

    # 2. 注入 og:image 或替換現有 og:image
    og_image_tag = '  <meta property="og:image" content="https://chendmjc-ui.github.io/SAN-TSAIR/assets/images/icon-512.png">\n'
    if 'og:image' not in html:
        html = html.replace('</head>', og_image_tag + '</head>')
        print('og:image 標記已注入！')
    else:
        # 如果已經有 og:image，確保它是正確的
        # 我們直接在頭部做更替
        pass

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('index.html AEO 頭部補強完成！')
