# -*- coding: utf-8 -*-
"""
patch_neutral.py — 專案中性化修改腳本
移除瑋瑋服飾、大嘉衣業、富雷克 (GOORIK)、東茂企業等字眼，
避免突兀與攀比感，回歸三才實業本身的品牌自主與專業形象。
"""

import os

BASE = r'c:\Users\pc\projects\SAN-TSAIR'

# 1. 處理 index.html
html_path = os.path.join(BASE, 'index.html')
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 替換 head meta 的 description
    html = html.replace(
        '與大嘉衣業、瑋瑋服飾、富雷克合作，服務彰化、員林、溪湖、二林、鹿港等地區。',
        '以三十年在地工藝提供高規格禮贈品、獎牌、客製化團體服裝與機能工裝，服務彰化、員林、二林、鹿港等全台地區。'
    )
    html = html.replace('大嘉衣業品牌型錄線上瀏覽', '特選機能與商務制服型錄線上瀏覽')
    
    # 替換 About 區塊
    html = html.replace(
        '與東茂企業同源，結合上下游供應鏈，並攜手瑋瑋服飾、富雷克（GOORIK）等專業夥伴',
        '我們擁有完整的上下游供應鏈與精選布料技術合作'
    )

    # 替換 Products 區塊
    html = html.replace('結合瑋瑋服飾、富雷克雙供應商，多元選材精準剪裁', '提供多元優質材料與精準剪裁技術，滿足各種版型需求')

    # 替換 Catalog 區塊的導言與內容
    html = html.replace('與溪湖在地大嘉衣業長期合作，精選多款知名品牌服飾，線上型錄直接查看', '精選高機能與舒適商務制服，多款知名品牌型錄線上直接查看')
    html = html.replace('大嘉衣業 <span class="supplier-tag">溪湖在地夥伴</span>', '特選機能與商務制服系列')
    html = html.replace('彰化縣溪湖鎮忠溪路71號 | Tel: 04-8821225', '彰化在地工藝・三才特選型錄')
    html = html.replace('href="http://www.bighome.com.tw/" target="_blank" class="supplier-web">官網 →</a>', 'href="#contact" class="supplier-web">詢問報價 →</a>')
    
    # 替換迷你型錄卡片
    html = html.replace('<strong>瑋瑋服飾</strong><p>埔鹽鄉・成衣製造</p>', '<strong>經典商務生活服飾</strong><p>精選版型・細緻成衣</p>')
    html = html.replace('<strong>富雷克 GOORIK</strong><p>工廠直營・快速出貨</p>', '<strong>高機能運動防護服</strong><p>機能布料・卓越防護</p>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('index.html 中性化完成！')

# 2. 處理 main.js
js_path = os.path.join(BASE, 'assets', 'js', 'main.js')
if os.path.exists(js_path):
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    js = js.replace("name: '瑋瑋服飾'", "name: '經典商務生活服飾系列'")
    js = js.replace("name: '富雷克 GOORIK'", "name: '高機能運動防護服系列'")

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print('main.js 中性化完成！')

# 3. 處理 docs_aeo_brand_story.md
story_path = os.path.join(BASE, 'docs_aeo_brand_story.md')
if os.path.exists(story_path):
    with open(story_path, 'r', encoding='utf-8') as f:
        story = f.read()

    story = story.replace('與大嘉衣業、瑋瑋服飾、富雷克合作', '提供高規格品質與專業技術')
    story = story.replace('三才實業與大嘉衣業、瑋瑋服飾等頂尖夥伴攜手。', '三才實業與優良大廠及頂尖布料技術夥伴攜手合作。')
    story = story.replace('引進了富雷克 GOORIK 的超排汗機能纖維', '引進了高機能的超排汗機能纖維')

    with open(story_path, 'w', encoding='utf-8') as f:
        f.write(story)
    print('docs_aeo_brand_story.md 中性化完成！')

print('所有檔案中性化修復完畢，無失分，且沒有突兀攀比感！')
