#!/usr/bin/env python3
"""Render the README's typography as self-contained SVGs.

GitHub strips CSS and web fonts from READMEs, so every piece of text outside
the banner is drawn as outlines here (text -> SVG paths). The output does not
depend on fonts installed on the viewer's machine.

Fonts (SIL OFL 1.1, not vendored):
  npm pack @fontsource-variable/archivo @fontsource/courier-prime
and point --fonts at the folder holding the extracted packages.

  pip install fonttools brotli
  python3 tools/typeset.py --fonts /path/to/fonts
"""
import argparse, io, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "type")

BG, EDGE, RULE = "#100e17", "#38303f", "#55415e"
INK, DIM, ACCENT = "#e5d6f7", "#aaa0b5", "#cfb0e9"
SHADE = {"░": 0.14, "▒": 0.3, "▓": 0.52, "█": 1.0}

PROMPT = "guest@hadez:~$ "
TERMINAL = r'''guest@hadez:~$ cat /etc/motd

            .         .
             _.-----._
         (@)=( . : . )=(@)
             '-.___.-'
  _..--"""--..|▓▓▓▓▓|..--"""--.._
.'░░░░░▒▒▒▒▒▒▒[▓▓X▓▓]▒▒▒▒▒▒▒░░░░░'.
'-._░░░▒▒▒_..-|▓▓▓▓▓|-.._▒▒▒░░░_.-'
    ""-..-""  \▓▓3▓▓/  ""-..-""
    .-'░▒▒'-.  |▓3▓|  .-'▒▒░'-.
    '-.░▒▒.-'  |▓0▓|  '-.▒▒░.-'
               '.1.'
                 V

guest@hadez:~$ finger hadez
Login: hadezkz002     Name: Hadez
Project: you ran the key.
Plan:
  typescript   react     next.js
  python       fastapi   node.js
  postgresql   docker    git

guest@hadez:~$ cat ~hadez/.signal
WMNJX YJABA VTJVB ZXYJX NMIKJ
FGKPV RMAZG FQWAI LRWIP ZIIYP
RHEES MEYTV QTFOX CTERX GRXMV
ZWYFB JUJZA MFOBZ YTVYX VSBBU
RVCWE CLRYG BAWVJ QGJMM NLRYX
NT

guest@hadez:~$ ls ~hadez/signal
0x01.wav
0x02.pub
0x03.png -> (sleeping)
0x04.gif -> (sleeping)

guest@hadez:~$ █'''

HERO_LINES = ["Builds web apps.", "Automates the repetitive parts.", "Cares how things look and feel."]
FOOTER = ["bGVzcyBub2lzZS4gbW9yZSBpbnRlbnQu",
          "the puzzles are original. the cicada and 3301 are a nod",
          "to puzzle culture — no affiliation."]


class Face:
    def __init__(self, font, tag="f"):
        self.font = font
        self.tag = tag
        self.upm = font["head"].unitsPerEm
        self.cmap = font.getBestCmap()
        self.glyphs = font.getGlyphSet()
        self.hmtx = font["hmtx"]

    def advance(self, ch, size):
        return self.hmtx[self.cmap[ord(ch)]][0] * size / self.upm

    def width(self, text, size, tracking=0.0):
        return sum(self.advance(c, size) for c in text) + tracking * size * (len(text) - 1)

    def glyph_id(self, ch):
        return f"{self.tag}{ord(ch):x}"

    def path(self, text, x, y, size, tracking=0.0):
        """Outline `text` with its baseline at (x, y); returns SVG path data."""
        s = size / self.upm
        out = []
        for ch in text:
            name = self.cmap.get(ord(ch))
            if name is None:
                raise KeyError(f"glyph missing: {ch!r}")
            pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            if pen.getCommands():
                out.append(pen.getCommands())
            x += self.advance(ch, size) + tracking * size
        return "".join(out)


def load_faces(fonts):
    mono = TTFont(os.path.join(fonts, "_fontsource_courier-prime/package/files/courier-prime-latin-400-normal.woff2"))
    mono_b = TTFont(os.path.join(fonts, "_fontsource_courier-prime/package/files/courier-prime-latin-700-normal.woff2"))
    var = TTFont(os.path.join(fonts, "_fontsource-variable_archivo/package/files/archivo-latin-standard-normal.woff2"))
    display = instantiateVariableFont(var, {"wght": 800, "wdth": 125})
    buf = io.BytesIO()
    display.flavor = None
    display.save(buf)
    buf.seek(0)
    return Face(mono, "m"), Face(mono_b, "b"), Face(TTFont(buf), "d")


def set_text(face, text, x, y, size, defs, fill, tracking=0.0):
    """Place `text` as <use> refs to glyphs defined once per face and size."""
    out = []
    for ch in text:
        if ch != " ":
            gid = f"{face.glyph_id(ch)}s{round(size * 10)}"
            defs.setdefault(gid, face.path(ch, 0, 0, size))
            out.append(f'<use href="#{gid}" x="{x:.2f}" y="{y:.2f}"/>')
        x += face.advance(ch, size) + tracking * size
    return f'<g fill="{fill}">' + "".join(out) + "</g>"


def with_defs(defs, body):
    return ["<defs>" + "".join(f'<path id="{k}" d="{d}"/>' for k, d in defs.items()) + "</defs>", *body]


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}">\n<title>{title}</title>\n{body}\n</svg>\n')


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_terminal(mono, mono_b):
    size, lh, pad, bar = 15, 21, 26, 34
    cw = mono.advance("a", size)
    lines = TERMINAL.split("\n")
    cols = max(len(l) for l in lines)
    w = round(pad * 2 + cols * cw)
    h = round(bar + pad + len(lines) * lh + pad - 6)
    defs, uses, blocks = {}, [], []
    for i, line in enumerate(lines):
        base = bar + pad + i * lh + size * 0.75
        top = bar + pad + i * lh - (lh - size) / 2 - 1
        is_prompt = line.startswith(PROMPT)
        for j, ch in enumerate(line):
            x = pad + j * cw
            if ch in SHADE:
                blocks.append(f'<rect x="{x:.2f}" y="{top:.2f}" width="{cw + 0.3:.2f}" height="{lh + 0.3}" '
                              f'fill-opacity="{SHADE[ch]}"/>')
                continue
            if ch == " ":
                continue
            if is_prompt:
                face, col = mono_b, (ACCENT if j < len(PROMPT) else INK)
            else:
                face, col = mono, (INK if 0 < i < 14 else DIM)
            gid = face.glyph_id(ch)
            defs.setdefault(gid, face.path(ch, 0, 0, size))
            uses.append(f'<use href="#{gid}" x="{x:.2f}" y="{base:.2f}" fill="{col}"/>')
    label = mono.path("hadez — tty1", pad, 22, 12, 0.08)
    body = [
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>',
        f'<path d="M1 {bar}H{w - 1}" stroke="{EDGE}"/>',
        f'<path fill="{DIM}" d="{label}"/>',
        *[f'<circle cx="{w - pad - k * 14}" cy="17" r="3.5" fill="none" stroke="{RULE}"/>' for k in range(3)],
        "<defs>" + "".join(f'<path id="{k}" d="{d}"/>' for k, d in defs.items()) + "</defs>",
        f'<g fill="{ACCENT}">' + "".join(blocks) + "</g>",
        *uses,
    ]
    return svg(w, h, esc(TERMINAL.replace("█", "_")), "\n".join(body))


def build_hero(mono, display):
    w, h, pad = 600, 330, 34
    size = 27
    widest = max(display.width(t, size, -0.01) for t in HERO_LINES)
    size = min(size, size * (w - pad * 2) / widest)
    defs = {}
    body = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>',
            set_text(mono, "$ whoami", pad, 70, 15, defs, ACCENT)]
    for k, t in enumerate(HERO_LINES):
        body.append(set_text(display, t, pad, 128 + k * size * 1.32, size, defs, INK, -0.01))
    body.append(f'<path d="M{pad} {h - 74}H{w - pad}" stroke="{EDGE}"/>')
    body.append(set_text(mono, "full-stack / ai workflows / visual experiments", pad, h - 44, 14, defs, DIM, 0.04))
    return svg(w, h, esc("$ whoami — " + " ".join(HERO_LINES) + " full-stack / ai workflows / visual experiments"),
               "\n".join(with_defs(defs, body)))


def build_footer(mono):
    w, h = 460, 92
    defs = {}
    body = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>']
    for k, (t, size, col) in enumerate(zip(FOOTER, (14, 12, 12), (ACCENT, DIM, DIM))):
        tw = mono.width(t, size, 0.04)
        body.append(set_text(mono, t, (w - tw) / 2, 34 + k * 22, size, defs, col, 0.04))
    return svg(w, h, esc(" ".join(FOOTER)), "\n".join(with_defs(defs, body)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True, help="folder with the extracted @fontsource packages")
    fonts = ap.parse_args().fonts
    mono, mono_b, display = load_faces(fonts)
    os.makedirs(OUT, exist_ok=True)
    for name, content in (("terminal.svg", build_terminal(mono, mono_b)),
                          ("hero.svg", build_hero(mono, display)),
                          ("footer.svg", build_footer(mono))):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{name}: {len(content) // 1024} KB")


if __name__ == "__main__":
    main()
