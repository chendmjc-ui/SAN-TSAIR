import re

BASE = r'c:\Users\pc\projects\SAN-TSAIR'
html_path = BASE + r'\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替換 gold-text -> accent-text (安全檢查)
content = content.replace('gold-text', 'accent-text')

# 2. 在 </head> 前注入 JSON-LD + PWA
pwa_jsonld = '''  <!-- PWA -->
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#1C1917">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="三才實業">

  <!-- JSON-LD LocalBusiness Schema AEO/SEO -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": "https://chendmjc-ui.github.io/SAN-TSAIR/#business",
    "name": "三才實業",
    "alternateName": ["三才禮贈品", "SAN-TSAIR"],
    "description": "彰化溪湖30年在地品牌，專業匾額、獎牌、錦旗、團體制服、訂製服裝、宮廟禮品一站式服務",
    "url": "https://chendmjc-ui.github.io/SAN-TSAIR/",
    "telephone": "+886-4-8821225",
    "email": "santsair@example.com",
    "foundingDate": "1995",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "溪湖鎮",
      "addressLocality": "溪湖鎮",
      "addressRegion": "彰化縣",
      "postalCode": "516",
      "addressCountry": "TW"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 23.9553,
      "longitude": 120.4651
    },
    "openingHoursSpecification": [
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
        "opens": "09:00",
        "closes": "18:00"
      }
    ],
    "priceRange": "$$",
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "禮贈品與制服服務目錄",
      "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "匾額製作", "description": "實木、壓克力、金屬匾額，燙金雷雕彩繪工藝"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "獎牌獎座", "description": "金銀銅獎牌、水晶獎座、錦旗製作"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "團體制服訂製", "description": "企業POLO衫、工作背心、班服、宮廟背心"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "訂製服裝", "description": "量身訂製，科技廠潔淨室規格服裝"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "企業禮贈品", "description": "開幕禮品、股東會紀念品、節慶禮盒"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "宮廟宗教禮品", "description": "錦旗令旗、神明馬甲、進香背心、建醮紀念品"}}
      ]
    },
    "areaServed": [
      {"@type": "City", "name": "溪湖鎮", "containedInPlace": {"@type": "State", "name": "彰化縣"}},
      {"@type": "City", "name": "員林市"},
      {"@type": "City", "name": "彰化市"},
      {"@type": "City", "name": "二林鎮"},
      {"@type": "City", "name": "鹿港鎮"},
      {"@type": "City", "name": "北斗鎮"},
      {"@type": "City", "name": "埔鹽鄉"},
      {"@type": "City", "name": "永靖鄉"}
    ],
    "knowsAbout": ["匾額", "獎牌", "制服訂製", "企業禮品", "宮廟禮品", "彰化禮品", "溪湖制服"],
    "slogan": "30年工藝堅持，從彰化出發，傳遞每一份榮耀"
  }
  </script>
</head>'''

if '<link rel="manifest"' not in content:
    content = content.replace('</head>', pwa_jsonld)
    print('JSON-LD + PWA injected')
else:
    print('Already has PWA/JSON-LD, skipping')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('index.html updated successfully')
print(f'File size: {len(content)} chars')
