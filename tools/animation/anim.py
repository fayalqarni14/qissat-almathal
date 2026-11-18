import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, features

FPS = 30
W, H = 1080, 1920
P = "/home/claude/anim/png"
OVER = Image.open("/home/claude/design/overlay.png").convert("RGBA")
FONT = ImageFont.truetype("/home/claude/design/brando.ttf", 44, layout_engine=ImageFont.Layout.RAQM)

VOICE = [
    ["عالم من كبار علماء اللغة...", "سمع مثل وما فهمه", "لين فهّمته الغربان!"],
    ["(الأصمعي) كان يسمع مثل يقول:", "\"وعلى أُلّافها الطيرُ تقع\"", "وما عرف وش معناه"],
    ["لين شاف غربان تنزل على الأرض:", "البُقع مع البُقع...", "والسود مع السود"],
    ["وبعدين نزل غراب أعرج...", "وجا غراب ثاني مكسور الجناح، ونزل جنبه"],
    ["ما جمعهم اللون هالمرة... جمعهم الحال!", "وهنا فهم الأصمعي المثل، وعرف إنه ما ضاع"],
    ["و\"أُلّافها\" يعني: اللي تألفهم وتستأنس فيهم", "واليوم صرنا نقول \"أشكالها\"... والمعنى واحد"],
    ["وهذي هي قصة مثل", "\"الطيور على أشكالها تقع\"", "وتنقال إذا اجتمع ناس متشابهين في طباعهم، في الخير وفي غيره"],
]
NTEXT = [2, 1, 2, 2, 2, 3, 1]
WPS = 2.3  # words per second, calm narration


def wc(s):
    return len(s.split())


import json, os
REAL = json.load(open("/home/claude/tts/lines/durations.json")) if os.path.exists("/home/claude/tts/lines/durations.json") else None
lines_t = []  # per scene: list of (start,end,line)
DUR = []
for si, v in enumerate(VOICE):
    t, seg = 0.6, []
    for li, ln in enumerate(v):
        d = REAL[si][li] if REAL else wc(ln) / WPS
        seg.append((t, t + d, ln))
        t += d + 0.45
    DUR.append(max(t + 0.9, 4.0))
    lines_t.append(seg)

scenes = [Image.open(f"{P}/s{i+1}.png").convert("RGB") for i in range(7)]
texts = [[Image.open(f"{P}/t{i+1}_{k}.png").convert("RGBA") for k in range(1, NTEXT[i] + 1)] for i in range(7)]

# reveal times for text items: spread over the voice lines
reveal = []
for i in range(7):
    n = NTEXT[i]
    segs = lines_t[i]
    rt = [segs[min(j, len(segs) - 1)][0] + (0.2 if j == 0 else 0) for j in range(n)]
    if i == 5:  # swap first, then meaning, then today
        rt = [0.3, segs[0][0] + 0.4, segs[1][0] + 0.2]
    reveal.append(rt)

starts = np.cumsum([0] + DUR[:-1])
TOTAL = sum(DUR)

# crumpled paper shape
rnd = random.Random(4)
NV = 13
verts = [(2 * math.pi * k / NV + rnd.uniform(-.15, .15), rnd.uniform(.72, 1.0)) for k in range(NV)]
shades = [rnd.randint(214, 252) for _ in range(NV)]


def paper(s, rot):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if s <= 0.01:
        return lay
    d = ImageDraw.Draw(lay)
    cx, cy, R = W / 2, H / 2, 1250 * s
    pts = [(cx + R * r * math.cos(a + rot), cy + R * r * math.sin(a + rot) * 1.15) for a, r in verts]
    d.polygon([(p[0] + 10, p[1] + 14) for p in pts], fill=(0, 0, 0, 70))
    for k in range(NV):
        a, b = pts[k], pts[(k + 1) % NV]
        g = shades[k]
        d.polygon([(cx, cy), a, b], fill=(g, g, g - 4, 255))
        d.line([(cx, cy), a], fill=(g - 30, g - 30, g - 34, 255), width=2)
    return lay


def caption(line):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bb = d.textbbox((0, 0), line, font=FONT, direction="rtl", language="ar")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W - tw) / 2, 1585
    d.rounded_rectangle([x - 26, y - 14, x + tw + 26, y + th + 26], 14, fill=(20, 12, 8, 165))
    d.text((x - bb[0], y - bb[1] + 4), line, font=FONT, fill=(255, 255, 255, 255), direction="rtl", language="ar")
    return lay


cap_cache = {}


def frame_at(t):
    i = int(np.searchsorted(starts, t, side="right") - 1)
    lt = t - starts[i]
    # ken burns
    z = 1.0 + 0.07 * (lt / DUR[i])
    sw, sh = int(W / z), int(H / z)
    dx = int((W - sw) / 2 + (8 if i % 2 else -8) * lt / DUR[i])
    img = scenes[i].crop((dx, (H - sh) // 2, dx + sw, (H - sh) // 2 + sh)).resize((W, H), Image.BILINEAR).convert("RGBA")
    img.alpha_composite(OVER)
    # text crossfade
    rt = reveal[i]
    shown = sum(1 for r in rt if lt >= r)
    if shown:
        cur = texts[i][shown - 1]
        a = min(1, (lt - rt[shown - 1]) / 0.45)
        if shown > 1 and a < 1:
            img.alpha_composite(Image.blend(texts[i][shown - 2], cur, a))
        elif a < 1:
            c = cur.copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * a))); img.alpha_composite(c)
        else:
            img.alpha_composite(cur)
    # caption (scratch VO text)
    for (s0, s1, ln) in lines_t[i]:
        if s0 <= lt < s1:
            if ln not in cap_cache:
                cap_cache[ln] = caption(ln)
            img.alpha_composite(cap_cache[ln])
    # paper transition around boundaries
    for b in starts[1:]:
        if abs(t - b) < 0.3:
            p = (t - (b - 0.3)) / 0.6
            img.alpha_composite(paper(math.sin(math.pi * p) * 1.05, p * 1.2))
    return img.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(n):
        ff.stdin.write(frame_at(f / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    import wave
    sr = 22050
    track = np.zeros(int((TOTAL + 1) * sr), dtype=np.float32)
    for si, seg in enumerate(lines_t):
        for li, (s0, s1, ln) in enumerate(seg):
            w = wave.open(f"/home/claude/tts/lines/{si+1}_{li+1}.wav")
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
            p = int((starts[si] + s0) * sr); track[p:p + len(a)] += a
    w = wave.open("/home/claude/anim/vo.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(track[:int(TOTAL * sr)], -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    print("durations", [round(d, 1) for d in DUR], "total", round(TOTAL, 1))
