"""Builds the 7 frames of «الطيور على أشكالها تقع» as HTML+SVG (no paid tools)."""
import base64, os, json

D = os.path.dirname(os.path.abspath(__file__))
b64 = lambda p: base64.b64encode(open(os.path.join(D, p), 'rb').read()).decode()
OVERLAY = b64('overlay.png')
FONT = b64('brando.ttf')

# ---------- reusable shapes ----------
CROW = "M20,60 C25,45 45,38 62,40 C70,30 80,28 88,34 L99,38 L88,42 C86,49 80,55 72,59 C66,70 50,74 38,72 L16,82 L8,79 L22,70 C18,67 18,63 20,60 Z"
HOOD = "M28,63 C38,50 58,46 71,53 C69,63 56,71 40,71 C34,70 30,67 28,63 Z"
LEGS = '<path d="M44,71 L42,93 M56,70 L58,93 M38,93 L48,93 M53,93 L63,93" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
FLY = "M50,52 C40,40 24,30 2,30 C18,37 31,45 41,55 C35,57 31,60 29,64 L40,61 L47,63 C51,61 56,61 60,63 L71,61 L83,63 C79,57 71,55 63,55 C73,46 86,35 99,27 C77,28 62,39 50,52 Z"


def crow(x, y, s, flip=False, hood=False, legs=True, col="#0c0809", eye=True, extra=""):
    t = f"translate({x},{y}) scale({-s if flip else s},{s})" + (" translate(-100,0)" if flip else "")
    g = f'<g transform="{t}"><path d="{CROW}" fill="{col}"/>'
    if hood:
        g += f'<path d="{HOOD}" fill="#9a948c"/>'
    if legs:
        g += LEGS.format(c=col)
    if eye:
        g += '<circle cx="85" cy="36" r="1.6" fill="#d9c9a8"/>'
    return g + extra + "</g>"


def flyer(x, y, s, rot=0, col="#1a1416"):
    return f'<g transform="translate({x},{y}) rotate({rot}) scale({s})"><path d="{FLY}" fill="{col}"/></g>'


def scholar(x, y, s, flip=False, col="#2a1d16", hl="#c99a5c"):
    """standing scholar with turban & robe, ~ 100x260 units"""
    t = f"translate({x},{y}) scale({-s if flip else s},{s})"
    return f'''<g transform="{t}">
      <path d="M30,70 C30,50 70,50 70,70 L74,78 C60,84 40,84 26,78 Z" fill="{col}"/>
      <path d="M26,62 C24,36 76,36 74,62 C70,54 30,54 26,62 Z" fill="#e9dcc4"/>
      <path d="M24,60 C40,52 60,52 76,60 L76,66 C60,60 40,60 24,66 Z" fill="#d8c7a6"/>
      <path d="M36,78 C40,92 60,92 64,78 L66,96 C58,104 42,104 34,96 Z" fill="#efe6d6"/>
      <path d="M22,96 C20,80 80,80 78,96 L94,250 C70,262 30,262 6,250 Z" fill="{col}"/>
      <path d="M50,96 L50,252" stroke="{hl}" stroke-width="2" opacity=".35"/>
      <path d="M78,100 C88,140 86,170 70,190 L62,182 C72,166 74,140 66,112 Z" fill="{col}"/>
    </g>'''


def seated(x, y, s, col="#2b1e17", turban=True):
    t = f"translate({x},{y}) scale({s})"
    head = '<path d="M34,22 C32,4 68,4 66,22 C60,16 40,16 34,22 Z" fill="#e6d8bf"/>' if turban else ''
    return f'''<g transform="{t}"><circle cx="50" cy="30" r="15" fill="{col}"/>{head}
      <path d="M22,52 C22,40 78,40 78,52 L96,108 C70,118 30,118 4,108 Z" fill="{col}"/></g>'''


def sky(top, mid, bottom, sun=None):
    s = f'''<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{top}"/><stop offset=".55" stop-color="{mid}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>
      <radialGradient id="sun"><stop offset="0" stop-color="#fff3cf"/><stop offset=".25" stop-color="#ffd38a" stop-opacity=".9"/><stop offset="1" stop-color="#ffb35c" stop-opacity="0"/></radialGradient></defs>
      <rect width="1080" height="1920" fill="url(#sky)"/>'''
    s += '<rect width="1080" height="1300" filter="url(#clouds)" opacity=".55"/>'
    if sun:
        s += f'<circle cx="{sun[0]}" cy="{sun[1]}" r="{sun[2]}" fill="url(#sun)"/>'
    s += '<rect y="900" width="1080" height="600" fill="url(#haze)"/>'
    return s


def dunes(y, c1, c2, c3):
    return f'''<path d="M0,{y} C200,{y-60} 380,{y-30} 560,{y-70} C760,{y-110} 900,{y-40} 1080,{y-80} L1080,1920 L0,1920 Z" fill="{c1}"/>
      <path d="M0,{y+140} C260,{y+80} 420,{y+150} 640,{y+100} C820,{y+60} 940,{y+120} 1080,{y+90} L1080,1920 L0,1920 Z" fill="{c2}"/>
      <path d="M0,{y+330} C300,{y+280} 620,{y+360} 1080,{y+300} L1080,1920 L0,1920 Z" fill="{c3}"/>
      <rect y="{y-120}" width="1080" height="{1920-y+120}" filter="url(#soil)" opacity=".7"/>'''


def fort(x, y, s, col):
    return f'''<g transform="translate({x},{y}) scale({s})" fill="{col}">
      <rect x="0" y="40" width="300" height="80"/><rect x="20" y="0" width="50" height="120"/><rect x="230" y="10" width="50" height="110"/>
      <rect x="120" y="25" width="70" height="95"/>
      {''.join(f'<rect x="{20+i*10}" y="-8" width="6" height="10"/>' for i in range(5))}
      {''.join(f'<rect x="{230+i*10}" y="2" width="6" height="10"/>' for i in range(5))}
      <path d="M140,120 L140,80 C140,64 170,64 170,80 L170,120 Z" fill="#000" opacity=".35"/></g>'''


def palm(x, y, s, col):
    return f'''<g transform="translate({x},{y}) scale({s})" fill="{col}">
      <path d="M48,200 C50,140 52,90 56,40 L62,40 C60,90 58,140 58,200 Z"/>
      <path d="M58,40 C30,20 10,30 0,50 C20,34 40,34 58,44 Z M58,40 C80,16 104,22 116,42 C96,30 78,32 60,46 Z
               M58,40 C50,10 30,0 14,6 C34,10 46,22 56,42 Z M58,40 C70,8 92,2 108,10 C88,12 74,24 62,44 Z
               M58,42 C40,46 24,64 22,84 C34,64 46,54 60,48 Z M60,42 C80,48 94,66 94,86 C84,66 72,54 58,48 Z"/></g>'''


GRAIN = '''<filter id="clouds" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0016 .006" numOctaves="5" seed="7"/>
  <feColorMatrix values="0 0 0 0 1  0 0 0 0 .86  0 0 0 0 .62  0 0 0 1.4 -.7"/></filter>
  <filter id="soil" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".02 .09" numOctaves="4" seed="3"/>
  <feColorMatrix values="0 0 0 0 .22  0 0 0 0 .13  0 0 0 0 .07  0 0 0 .9 -.25"/></filter>
  <filter id="sepia"><feColorMatrix type="matrix" values="1.08 .12 0 0 .01  .06 .94 .02 0 0  0 .04 .72 0 -.02  0 0 0 1 0"/></filter>
  <filter id="soft"><feGaussianBlur stdDeviation="2.2"/></filter>
  <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d3a0" stop-opacity="0"/><stop offset=".5" stop-color="#f3d3a0" stop-opacity=".55"/><stop offset="1" stop-color="#f3d3a0" stop-opacity="0"/></linearGradient>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .42  0 0 0 0 .32  0 0 0 .55 0"/></filter>
  <radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1b0f08" stop-opacity=".65"/></radialGradient>'''
DIAMONDS = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" transform="rotate(45 {x+w/2} {y+w/2})" fill="#3ee0a8" opacity="{o}"/>' for x,y,w,o in [(70,520,22,.9),(96,640,14,.8),(60,760,18,.85),(110,880,10,.7),(74,1010,16,.8),(120,1150,9,.6),(64,1280,12,.75),(98,1420,8,.6),(130,1560,7,.5),(84,1700,10,.6)])
FINISH = '<rect width="1080" height="1920" filter="url(#grain)" opacity=".55"/><rect width="1080" height="1920" fill="url(#vig)"/>' + DIAMONDS

# ---------- scenes ----------
def s1():
    b = sky("#5b4a5e", "#d98c4f", "#f2b46b", sun=(820, 1020, 260))
    b += dunes(1180, "#a8683b", "#8a532f", "#5e3820")
    for i, (x, y, s, r) in enumerate([(180, 760, 1.4, -8), (380, 690, 1.0, 6), (560, 820, 1.6, -4), (700, 640, .8, 10), (300, 930, 1.2, 4), (860, 760, 1.1, -12), (480, 1000, .9, 8)]):
        b += flyer(x, y, s, r)
    b += crow(150, 1300, 1.5) + crow(330, 1330, 1.3, flip=True) + crow(880, 1320, 1.2, flip=True)
    # scholar in foreground (cropped, from behind / side)
    b += scholar(760, 1180, 2.3, flip=True, col="#22170f")
    return b


def s2():
    b = '<rect width="1080" height="1920" fill="#3a2516"/>'
    b += '<defs><linearGradient id="win" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe0a3" stop-opacity=".95"/><stop offset="1" stop-color="#f2a85a" stop-opacity="0"/></linearGradient></defs>'
    b += '<path d="M700,380 L900,380 L900,760 L700,760 Z" fill="#ffd99a" opacity=".85"/><path d="M700,380 L900,380 L1080,1500 L240,1500 Z" fill="url(#win)" opacity=".35"/>'
    b += '<path d="M700,380 L900,380 M800,380 L800,760 M700,570 L900,570" stroke="#3a2516" stroke-width="10"/>'
    b += '<rect y="1420" width="1080" height="500" fill="#5a3721"/><path d="M80,1500 L1000,1500 L1080,1920 L0,1920 Z" fill="#7a2f22"/>'
    b += ''.join(f'<path d="M{80+i*60},1500 L{40+i*70},1920" stroke="#a8553a" stroke-width="3" opacity=".5"/>' for i in range(15))
    b += seated(90, 1330, 2.1, "#2a1a10") + seated(820, 1330, 2.1, "#2a1a10") + seated(240, 1430, 1.8, "#1f140c") + seated(680, 1440, 1.8, "#1f140c")
    b += scholar(410, 1010, 2.3, col="#3b2a1e")
    return b


def s3():
    b = sky("#6a5363", "#e09a59", "#f4c07e", sun=(540, 1150, 300))
    b += dunes(1250, "#b9784a", "#9c613a", "#6e4327")
    # black group (right) / hooded group (left)
    for x, y, s, f in [(600, 1450, 1.3, True), (720, 1480, 1.5, True), (840, 1440, 1.2, True), (700, 1590, 1.6, True)]:
        b += crow(x, y, s, flip=f)
    for x, y, s in [(110, 1460, 1.3), (240, 1490, 1.5), (160, 1600, 1.6), (330, 1440, 1.1)]:
        b += crow(x, y, s, hood=True)
    b += scholar(470, 1180, 1.1, col="#3a2618")
    return b


def s4():
    b = sky("#4c3c4c", "#c9814c", "#e8a868", sun=(860, 820, 220))
    b += '<ellipse cx="540" cy="1560" rx="620" ry="260" fill="#8a5634"/><ellipse cx="540" cy="1640" rx="700" ry="300" fill="#6c4227"/>'
    lame = crow(170, 1250, 3.2, legs=False, extra='<path d="M50,71 L54,93 M49,93 L60,93" stroke="#141012" stroke-width="2.4" stroke-linecap="round"/><path d="M42,71 L36,80" stroke="#141012" stroke-width="2.4" stroke-linecap="round"/>')
    b += f'<g transform="rotate(-4 330 1400)">{lame}</g>'
    wing = '<path d="M44,52 C30,62 24,82 28,99 L37,92 C39,78 46,66 54,58 Z" fill="#1d1719"/>'
    b += crow(560, 1270, 3.2, flip=True, extra=wing)
    return b


def s5():
    b = sky("#56445a", "#d48e57", "#f0b878", sun=(300, 900, 260))
    b += dunes(1300, "#a86d42", "#8b5634", "#603a22")
    b += f'<g opacity=".9">{scholar(560, 760, 3.4, flip=True, col="#2a1c13")}</g>'
    b += '<path d="M380,1020 C400,1000 420,1000 440,1010" stroke="#e9d4b0" stroke-width="5" fill="none" opacity=".0"/>'
    b += crow(120, 1520, 2.2, legs=True) + crow(300, 1540, 2.2, flip=True, extra='<path d="M44,52 C30,62 24,82 28,99 L37,92 C39,78 46,66 54,58 Z" fill="#1d1719"/>')
    return b


def s6():
    b = sky("#3f3550", "#c37a4a", "#e6a463", sun=(540, 1180, 260))
    b += dunes(1300, "#93603b", "#7a4c2d", "#523220")
    b += '<ellipse cx="540" cy="1560" rx="120" ry="26" fill="#2a1a0f"/><path d="M500,1550 C520,1480 560,1480 580,1550 Z" fill="#ffb347"/><path d="M520,1552 C530,1500 550,1500 560,1552 Z" fill="#ffe08a"/>'
    for x, s in [(150, 2.0), (330, 2.2), (620, 2.2), (800, 2.0)]:
        b += seated(x, 1370, s, "#21150d", turban=False)
    b += '<g transform="translate(660,1520) scale(1.6)" fill="#c58a3a"><path d="M10,40 L30,40 L34,10 C34,0 6,0 6,10 Z"/><path d="M34,14 L50,4 L48,10 L34,22 Z"/></g>'
    return b


def s7():
    b = sky("#4a3a55", "#e08c4a", "#f6c27a", sun=(540, 1260, 360))
    b += fort(640, 1290, 1.2, "#5b3620") + palm(140, 1150, 1.6, "#3f2615") + palm(300, 1210, 1.2, "#4a2d18")
    b += dunes(1400, "#a36a40", "#86522f", "#5b371f")
    for x, y, s, r in [(200, 820, 1.6, -6), (360, 760, 1.3, 4), (520, 700, 1.7, -2), (680, 780, 1.4, 8), (820, 700, 1.1, -10), (430, 900, 1.2, 6), (610, 940, 1.0, -4), (300, 1010, .9, 10), (760, 990, .9, 2)]:
        b += flyer(x, y, s, r)
    return b


SCENES = [s1, s2, s3, s4, s5, s6, s7]

# ---------- text per frame (from the approved script's graphic column) ----------
TEXT = [
    [("line", "عالم لغة كبير…"), ("strip", "سمع مثل وما فهمه!")],
    [("strip", "«وعلى أُلّافها الطيرُ تقع»")],
    [("line", "البُقع مع البُقع…"), ("strip", "والسود مع السود")],
    [("line", "غراب أعرج…"), ("strip", "وجنبه غراب مكسور الجناح")],
    [("line", "ما جمعهم اللون…"), ("strip", "جمعهم الحال!")],
    [("swap", "أُلّافها", "أشكالها"), ("small", "أُلّافها = اللي تألفهم"), ("line", "واليوم نقول: أشكالها")],
    [("big", "الطيور على أشكالها تقع")],
]


def text_html(items):
    out = []
    for it in items:
        k = it[0]
        if k == "line":
            out.append(f'<div class="t line">{it[1]}</div>')
        elif k == "small":
            out.append(f'<div class="t small">{it[1]}</div>')
        elif k == "strip":
            out.append(f'<div class="strip"><span>{it[1]}</span></div>')
        elif k == "big":
            out.append(f'<div class="strip big"><span>{it[1]}</span></div>')
        elif k == "swap":
            out.append(f'<div class="swap"><span class="old">{it[1]}</span><span class="arrow">←</span><span class="new">{it[2]}</span></div>')
    return "\n".join(out)


CSS = f'''@font-face{{font-family:Brando;src:url(data:font/ttf;base64,{FONT}) format("truetype");}}
*{{margin:0;padding:0;box-sizing:border-box}}
.frame{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Brando,sans-serif;direction:rtl;background:#2a1a10}}
.frame svg.scene{{position:absolute;inset:0}}
.frame img.overlay{{position:absolute;inset:0;width:1080px;height:1920px}}
.txt{{position:absolute;top:330px;left:110px;right:110px;display:flex;flex-direction:column;align-items:center;gap:26px;text-align:center}}
.t{{color:#fff;font-weight:700;text-shadow:0 3px 14px rgba(20,10,4,.75),0 1px 2px rgba(0,0,0,.6);-webkit-text-stroke:1.2px #fff}}
.line{{font-size:78px;line-height:1.3}}
.small{{font-size:54px;line-height:1.35}}
.strip{{position:relative;padding:14px 46px 22px;}}
.strip:before{{content:"";position:absolute;inset:0;background:#e9dcc3;border-radius:6px;transform:rotate(-1.2deg);
  box-shadow:0 6px 18px rgba(0,0,0,.35);clip-path:polygon(0 8%,4% 0,30% 6%,55% 0,80% 7%,100% 2%,99% 92%,74% 100%,48% 93%,22% 100%,1% 94%)}}
.strip span{{position:relative;color:#2b1a12;font-size:76px;font-weight:700;-webkit-text-stroke:1.3px #2b1a12;line-height:1.3}}
.strip.big span{{font-size:86px;white-space:nowrap}}
.swap{{display:flex;align-items:center;gap:30px;font-size:84px;font-weight:700}}
.swap .old{{color:#e9dcc3;text-decoration:line-through;text-decoration-thickness:6px;text-decoration-color:#c0392b;-webkit-text-stroke:1.2px #e9dcc3;text-shadow:0 3px 12px rgba(0,0,0,.7)}}
.swap .new{{color:#fff;-webkit-text-stroke:1.2px #fff;text-shadow:0 3px 12px rgba(0,0,0,.7)}}
.swap .arrow{{color:#7fe0c4;font-size:70px}}
'''


def frame(i):
    svg = f'<svg class="scene" viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg"><defs>{GRAIN}</defs><g filter="url(#sepia)">{SCENES[i]()}</g>{FINISH}</svg>'
    return f'<div class="frame" id="f{i+1}">{svg}<img class="overlay" src="data:image/png;base64,{OVERLAY}"/><div class="txt">{text_html(TEXT[i])}</div></div>'


if __name__ == "__main__":
    os.makedirs(os.path.join(D, "html"), exist_ok=True)
    for i in range(7):
        html = f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{frame(i)}</body></html>'
        open(os.path.join(D, "html", f"frame{i+1}.html"), "w").write(html)
    print("ok")


def scene_only(i):
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="frame"><svg class="scene" viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg"><defs>{GRAIN}</defs>'
            f'<g filter="url(#sepia)">{SCENES[i]()}</g>{FINISH}</svg></div></body></html>')


def text_only(i, k):
    items = TEXT[i]
    parts = []
    for j, it in enumerate(items):
        h = text_html([it])
        parts.append(h if j < k else f'<div style="visibility:hidden">{h}</div>')
    css = CSS.replace("background:#2a1a10", "background:transparent")
    return (f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{css} html,body{{background:transparent}}</style></head><body>'
            f'<div class="frame"><div class="txt">{"".join(parts)}</div></div></body></html>')


def build_layers(out):
    os.makedirs(out, exist_ok=True)
    for i in range(7):
        open(f"{out}/s{i+1}.html", "w").write(scene_only(i))
        for k in range(1, len(TEXT[i]) + 1):
            open(f"{out}/t{i+1}_{k}.html", "w").write(text_only(i, k))
