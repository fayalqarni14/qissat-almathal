import os, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from episodes_batch1 import EPISODES  # ضع ملف الحلقات هنا

LOGO = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FONT = "Brando Arabic Regular"
RED = RGBColor(0xC0, 0x00, 0x00)


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), v)
    return e


def set_bidi(p):
    pPr = p._p.get_or_add_pPr()
    if pPr.find(qn('w:bidi')) is None:
        pPr.insert(0, el('w:bidi'))


def style_run(r, size, bold=False, color=None):
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    rPr = r._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rFonts.set(qn(a), FONT)
    rPr.append(el('w:szCs', **{'w:val': str(int(size * 2))}))
    if bold:
        rPr.append(el('w:bCs'))
    rPr.append(el('w:rtl'))
    if color:
        r.font.color.rgb = color


def para(container, text, size=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, parts=None, after=4):
    p = container.add_paragraph()
    set_bidi(p)
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    for t, c in (parts or [(text, None)]):
        style_run(p.add_run(t), size, bold, c)
    return p


def fill_cell(cell, lines, size=12, bold=False, align=WD_ALIGN_PARAGRAPH.RIGHT):
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    first = cell.paragraphs[0]
    first._p.getparent().remove(first._p)
    for line in lines:
        para(cell, line, size, bold, align, after=3)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(el('w:shd', **{'w:val': 'clear', 'w:color': 'auto', 'w:fill': hexcolor}))


def setup(doc):
    # Normal style: Arabic, RTL by default so any new paragraph is RTL
    st = doc.styles['Normal']
    st.font.name = FONT
    st.font.size = Pt(12)
    rPr = st.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rFonts.set(qn(a), FONT)
    rPr.append(el('w:szCs', **{'w:val': '24'}))
    rPr.append(el('w:rtl'))
    pPr = st.element.get_or_add_pPr()
    pPr.insert(0, el('w:bidi'))
    pPr.append(el('w:jc', **{'w:val': 'right'}))
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.2)
    sec._sectPr.append(el('w:bidi'))
    # logo in footer, left side (end of RTL line)
    fp = sec.footer.paragraphs[0]
    set_bidi(fp)
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.add_run().add_picture(LOGO, width=Cm(3.2))


def build(ep):
    doc = Document()
    setup(doc)
    body = doc
    doc.paragraphs[0]._p.getparent().remove(doc.paragraphs[0]._p) if doc.paragraphs else None
    para(body, "بسم الله الرحمن الرحيم", 14, True)
    para(body, None, 20, False, parts=[("المحتوى الخاص بحسابات \"", None), ("أخبار المجتمع", RED), ("\"", None)])
    para(body, f"قصة مثل : \"{ep['proverb']}\"", 16, True, after=10)

    headers = ["رقم المشهد", "النص الأساسي", "نص الجرافيك", "الصوت"]
    widths = [Cm(2.0), Cm(4.5), Cm(4.3), Cm(6.6)]
    t = doc.add_table(rows=1, cols=4)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    tblPr.append(el('w:bidiVisual'))
    t.autofit = False
    tblPr.append(el('w:tblLayout', **{'w:type': 'fixed'}))
    for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), widths):
        gc.set(qn('w:w'), str(int(w.twips)))
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.width = widths[i]
        fill_cell(c, [h], 12, True, WD_ALIGN_PARAGRAPH.CENTER)
        shade(c, 'E7E6E6')
    # repeat header row on new pages
    trPr = t.rows[0]._tr.get_or_add_trPr()
    trPr.append(el('w:tblHeader'))
    for n, (vis, gfx, voice) in enumerate(ep['scenes'], start=1):
        row = t.add_row()
        for i, w in enumerate(widths):
            row.cells[i].width = w
        fill_cell(row.cells[0], [str(n)], 12, True, WD_ALIGN_PARAGRAPH.CENTER)
        fill_cell(row.cells[1], vis, 11)
        fill_cell(row.cells[2], gfx, 12, True, WD_ALIGN_PARAGRAPH.CENTER)
        fill_cell(row.cells[3], voice, 12, True)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(el('w:cantSplit'))

    para(body, "", 8)
    para(body, "أساس الحلقة والتوثيق", 13, True, after=4)
    para(body, ep['basis'], 12, False, WD_ALIGN_PARAGRAPH.JUSTIFY, after=10)
    para(body, "المصادر", 13, True, after=4)
    for title, url in ep['sources']:
        para(body, title, 12, False, WD_ALIGN_PARAGRAPH.RIGHT, after=0)
        para(body, url, 11, False, WD_ALIGN_PARAGRAPH.RIGHT, after=8)
    if ep.get('note'):
        para(body, ep['note'], 12, True, WD_ALIGN_PARAGRAPH.RIGHT, after=0)
    path = os.path.join(OUT, ep['file'] + '.docx')
    doc.save(path)
    print('saved', path)


for ep in EPISODES:
    build(ep)
