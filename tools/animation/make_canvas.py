import json, os, datetime, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen

OVER = "/_blob/59d78951c682c82b8812e5a5159f5317"
FONT = "/_blob/59bca3c87f68f4dfe13ad34d6306bea3"
ROOT = "/home/claude/design/canvas/project"
os.makedirs(ROOT, exist_ok=True)

VOICE = [
    ["عالم من كبار علماء اللغة...", "سمع مثل وما فهمه", "لين فهّمته الغربان!"],
    ["(الأصمعي) كان يسمع مثل يقول:", "\"وعلى أُلّافها الطيرُ تقع\"", "وما عرف وش معناه"],
    ["لين شاف غربان تنزل على الأرض:", "البُقع مع البُقع...", "والسود مع السود"],
    ["وبعدين نزل غراب أعرج...", "وجا غراب ثاني مكسور الجناح، ونزل جنبه"],
    ["ما جمعهم اللون هالمرة... جمعهم الحال!", "وهنا فهم الأصمعي المثل، وعرف إنه ما ضاع"],
    ["و\"أُلّافها\" يعني: اللي تألفهم وتستأنس فيهم", "واليوم صرنا نقول \"أشكالها\"... والمعنى واحد"],
    ["وهذي هي قصة مثل", "\"الطيور على أشكالها تقع\"", "وتنقال إذا اجتمع ناس متشابهين في طباعهم، في الخير وفي غيره"],
]
TITLES = ["١ — الافتتاح", "٢ — المثل القديم", "٣ — الغربان", "٤ — الأعرج والمكسور", "٥ — جمعهم الحال", "٦ — المعنى", "٧ — المثل"]

SHADOW = "text-shadow: 0 3px 14px rgba(20,10,4,.75), 0 1px 2px rgba(0,0,0,.6)"
WHITE = f"color: #ffffff; font-weight: 700; -webkit-text-stroke: 1.2px #ffffff; {SHADOW}"
STRIP_BOX = ("display: inline-block; padding: 12px 44px 20px; background: #e9dcc3; border-radius: 6px; transform: rotate(-1.2deg); "
             "box-shadow: 0 6px 18px rgba(0,0,0,.35); clip-path: polygon(0 8%,4% 0,30% 6%,55% 0,80% 7%,100% 2%,99% 92%,74% 100%,48% 93%,22% 100%,1% 94%)")
STRIP_TXT = "color: #2b1a12; font-weight: 700; -webkit-text-stroke: 1.3px #2b1a12; line-height: 1.3"


def text_markup(items):
    out = []
    for it in items:
        k = it[0]
        if k == "line":
            out.append(f'<p style="margin: 0; font-size: 78px; line-height: 1.3; {WHITE}">{it[1]}</p>')
        elif k == "small":
            out.append(f'<p style="margin: 0; font-size: 54px; line-height: 1.35; {WHITE}">{it[1]}</p>')
        elif k in ("strip", "big"):
            size = 86 if k == "big" else 76
            out.append(f'<div style="{STRIP_BOX}"><span style="font-size: {size}px; white-space: nowrap; {STRIP_TXT}">{it[1]}</span></div>')
        elif k == "swap":
            out.append(
                '<div style="display: flex; align-items: center; gap: 30px; font-size: 84px; font-weight: 700">'
                f'<span style="color: #e9dcc3; text-decoration: line-through; text-decoration-thickness: 6px; text-decoration-color: #c0392b; {SHADOW}">{it[1]}</span>'
                '<span style="color: #7fe0c4; font-size: 70px">←</span>'
                f'<span style="color: #ffffff; -webkit-text-stroke: 1.2px #ffffff; {SHADOW}">{it[2]}</span></div>')
    return "\n".join(out)


def artboard(i):
    svg = (f'<svg aria-hidden="true" viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg" '
           f'style="position: absolute; left: 0; top: 0"><defs>{gen.GRAIN}</defs><g filter="url(#sepia)">{gen.SCENES[i]()}</g>{gen.FINISH}</svg>')
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>الطيور على أشكالها تقع — فريم {i+1}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
@font-face{{font-family:"Brando Arabic";src:url("{FONT}") format("truetype");}}
body{{margin:0}}
a{{color:#e9dcc3}}a:hover{{color:#ffffff}}
</style>
</helmet>
<div dir="rtl" style="position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #2a1a10; font-family: 'Brando Arabic', sans-serif">
{svg}
<img src="{OVER}" alt="" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1920px">
<div style="position: absolute; top: 330px; left: 110px; right: 110px; display: flex; flex-direction: column; align-items: center; gap: 26px; text-align: center">
{text_markup(gen.TEXT[i])}
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1080,"height":1920}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''


names = ["Main.dc.html"] + [f"Frame{i}.dc.html" for i in range(2, 8)]
boards, notes = {}, {}
for i, n in enumerate(names):
    x = i * 1160
    boards[n] = {"x": x, "y": 0, "w": 1080, "h": 1920, "title": f"فريم {TITLES[i]}"}
    notes[f"voice{i+1}"] = {"x": x, "y": 2040, "w": 1080, "size": "l", "fill": "orange",
                            "text": "الصوت:\n" + "\n".join(VOICE[i])}
    open(os.path.join(ROOT, n), "w").write(artboard(i))
notes["title"] = {"x": 0, "y": -320, "text": "قصة مثل: الطيور على أشكالها تقع — ٧ فريمات للمراجعة قبل التحريك", "kind": "title1", "maxW": 7960}
canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},
          "title": "قصة مثل — الطيور على أشكالها تقع (فريمات)", "launch": {"view": "canvas"}, "pages": [],
          "boards": boards, "order": names, "notes": notes, "designSystems": []}
json.dump(canvas, open(os.path.join(ROOT, "canvas.json"), "w"), ensure_ascii=False, indent=1)
print(names)
