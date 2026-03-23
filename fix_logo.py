import base64, re

with open('logo.png', 'rb') as f:
    b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

with open('index.html') as f:
    html = f.read()

html = re.sub(
    r'<div class="login-logo">.*?</div>',
    '<div class="login-logo"><img src="' + b64 + '" style="height:44px;border-radius:10px"><div style="margin-left:10px"><div style="font-size:18px;font-weight:700;color:white">KOSHER</div><div style="font-size:11px;color:#4ade80;letter-spacing:2px">WITHOUT BORDERS</div></div></div>',
    html, flags=re.DOTALL
)

html = re.sub(
    r'<div class="nav-logo">.*?</div>',
    '<div class="nav-logo" onclick="showScreen(\'dashboard\')" style="cursor:pointer"><img src="' + b64 + '" style="height:34px;border-radius:8px"><span style="margin-left:8px;font-size:14px;font-weight:600">KOSHER <span style="color:#4ade80">WITHOUT BORDERS</span></span></div>',
    html, flags=re.DOTALL
)

with open('index.html', 'w') as f:
    f.write(html)

print('Done! Logo instances:', html.count('data:image/png'))
