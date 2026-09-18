import re

# Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('請搜尋「三才禮贈品」', '請加入 ID：<a href="https://line.me/R/ti/p/@669vddce" target="_blank" class="accent-text" style="font-weight:700;">@669vddce</a>')

if 'line-float-btn' not in content:
    line_btn = '''
<!-- Floating LINE Button -->
<a href="https://line.me/R/ti/p/@669vddce" target="_blank" class="line-float-btn" aria-label="加入 LINE 官方帳號">
  <img src="https://upload.wikimedia.org/wikipedia/commons/4/41/LINE_logo.svg" alt="LINE" style="width: 32px; height: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">
</a>
'''
    content = content.replace('</body>', line_btn + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Update style.css
with open('assets/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

if 'line-float-btn' not in css:
    css += '''
.line-float-btn {
  position: fixed;
  bottom: 80px;
  right: 16px;
  background: #00B900;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 185, 0, 0.4);
  z-index: 998;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.line-float-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 16px rgba(0, 185, 0, 0.5);
}
@media(max-width:768px){
  .line-float-btn { bottom: 80px; }
}
'''
    with open('assets/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    
    css_min = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    css_min = re.sub(r'\s+', ' ', css_min).replace('{ ', '{').replace(' }', '}').replace(': ', ':').replace('; ', ';')
    with open('assets/css/style.min.css', 'w', encoding='utf-8') as f:
        f.write(css_min.strip())

print('LINE ID integration completed.')
