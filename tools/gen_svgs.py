#!/usr/bin/env python3
"""Generates the site's diagrams as inline SVG partials (src/partials/svg/*.svg).
Visual language matches the 'How MemChip works' video: lilac bilayer, grey tethers and electrode, teal signal."""
import math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'partials', 'svg')
os.makedirs(OUT, exist_ok=True)

TEAL='#00A8AB'; TEALD='#008a8c'; MINT='#B4E0DE'; PERI='#637AB9'; INDIGO='#3D316D'; INK='#1C1B2A'; MUTED='#6B6A78'
HEAD='#E3CBE2'; HEADS='#C9A9C8'; TAIL='#CFC8DA'; ELEC='#DCDBE2'; TETH='#A9A7B5'; PEP='#C2536B'; CH='#5D6FB8'
FONT="font-family:'DM Mono',monospace"

def bilayer(x0, x1, y, n, gap=None, r=4.2, tail=11, tethers=True, elec=True):
    s = []
    if elec:
        s.append(f'<rect x="{x0-8}" y="{y+tail*2+22}" width="{x1-x0+16}" height="9" rx="4.5" fill="{ELEC}"/>')
    st = (x1-x0)/n
    for i in range(n+1):
        x = x0+i*st
        if gap and gap[0] < x < gap[1]: continue
        for d, yy in ((1, y), (-1, y+tail*2+6)):
            s.append(f'<path d="M{x-1.6:.1f} {yy+d*r:.1f}q-1.2 {d*tail/2:.1f} 0 {d*tail:.1f}M{x+1.6:.1f} {yy+d*r:.1f}q1.2 {d*tail/2:.1f} 0 {d*tail:.1f}" stroke="{TAIL}" stroke-width="1.3" fill="none"/>')
            s.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r}" fill="{HEAD}" stroke="{HEADS}" stroke-width=".8"/>')
    if tethers and elec:
        for i in range(2, n, 5):
            x = x0+i*st
            if gap and gap[0]-6 < x < gap[1]+6: continue
            yb = y+tail*2+6+r
            s.append(f'<path d="M{x:.1f} {y+tail*2+22} c-3 -4 3 -7 0 -{(y+tail*2+22-yb):.1f}" stroke="{TETH}" stroke-width="1.4" fill="none"/>')
    return ''.join(s)

def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">{body}</svg>'

def text(x, y, t, size=11, fill=MUTED, anchor='start', weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" style="{FONT}">{t}</text>'

def trace(x0, y0, w, h, kind, color=TEAL, axis=True, marker=None):
    """Mini chart. kind: flat, rise, step, sigmoid, endpoint, decay"""
    s = []
    if axis:
        s.append(f'<path d="M{x0} {y0} V{y0+h} H{x0+w}" stroke="{TETH}" stroke-width="1.2" fill="none"/>')
    pts = []
    for i in range(61):
        t = i/60
        if kind == 'flat': v = .2
        elif kind == 'rise': v = .15+.7*(1-math.exp(-max(0, t-.3)*6)) if t > .3 else .15
        elif kind == 'sigmoid': v = .15+.7/(1+math.exp(-(t-.55)*16))
        elif kind == 'step': v = .2 if t < .45 else .75
        elif kind == 'decay': v = .85-.65/(1+math.exp(-(t-.5)*14))
        else: v = .2
        pts.append((x0+4+t*(w-8), y0+h-4-v*(h-8)))
    if kind == 'endpoint':
        s.append(f'<circle cx="{x0+w-14}" cy="{y0+h*.35}" r="5" fill="{color}"/>')
        s.append(f'<path d="M{x0+4} {y0+h-4} H{x0+w-24}" stroke="{TAIL}" stroke-width="1.4" stroke-dasharray="3 4"/>')
    else:
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        s.append(f'<path d="{d}" stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        x, y = pts[-1]
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{color}"/>')
    if marker is not None:
        mx = x0+4+marker*(w-8)
        s.append(f'<path d="M{mx:.1f} {y0+6} V{y0+h}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 3"/>')
    return ''.join(s)

def arrow(x0, y, x1):
    return (f'<path d="M{x0} {y} H{x1-8}" stroke="{TEAL}" stroke-width="2" stroke-dasharray="5 5"/>'
            f'<path d="M{x1-10} {y-6} L{x1} {y} L{x1-10} {y+6}" stroke="{TEAL}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

def lnp(cx, cy, r=18):
    s = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#F6EEF6" stroke="{HEADS}" stroke-width="2.2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r-5}" fill="none" stroke="{HEAD}" stroke-width="1.6"/>']
    for k in range(3):
        y = cy-6+k*6
        s.append(f'<path d="M{cx-8} {y} q4 -3 8 0 t8 0" stroke="{PERI}" stroke-width="1.3" fill="none"/>')
    return ''.join(s)

def peptide(cx, cy, ang=0, color=PEP):
    return (f'<g transform="rotate({ang} {cx} {cy})"><path d="M{cx-14} {cy} q3.5 -6 7 0 t7 0 t7 0 t7 0" stroke="{color}" stroke-width="3" fill="none" stroke-linecap="round"/></g>')

def channel(cx, y, open_=False):
    s = [f'<rect x="{cx-17}" y="{y}" width="14" height="40" rx="6" fill="{CH}"/>',
         f'<rect x="{cx+3}" y="{y}" width="14" height="40" rx="6" fill="{CH}"/>']
    if open_:
        s.insert(0, f'<rect x="{cx-4}" y="{y-6}" width="8" height="52" fill="{TEAL}" opacity=".35"/>')
    else:
        s.append(f'<rect x="{cx-4}" y="{y+14}" width="8" height="12" rx="2" fill="{CH}"/>')
    return ''.join(s)

files = {}

# ---- home: four steps (icons) ----
def icon_wrap(body, label):
    return svg(96, 96, f'<circle cx="48" cy="48" r="46" fill="#fff" stroke="{MINT}" stroke-width="2"/>{body}', label)
files['step-form'] = icon_wrap(
    f'<circle cx="36" cy="30" r="9" fill="#F6EEF6" stroke="{HEADS}" stroke-width="2"/><circle cx="58" cy="24" r="7" fill="#F6EEF6" stroke="{HEADS}" stroke-width="2"/>'
    + bilayer(22, 74, 50, 8, r=3, tail=6, tethers=False, elec=False) + f'<rect x="20" y="70" width="56" height="5" rx="2.5" fill="{ELEC}"/>', 'Form the membrane')
files['step-add'] = icon_wrap(
    f'<path d="M44 14 h8 v22 l-4 10 l-4 -10z" fill="#fff" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    f'<circle cx="48" cy="54" r="3.4" fill="{PEP}"/><circle cx="40" cy="62" r="3" fill="{PERI}"/><circle cx="56" cy="61" r="3" fill="{TEAL}"/>'
    + bilayer(22, 74, 68, 8, r=3, tail=4, tethers=False, elec=False), 'Add your sample')
files['step-read'] = icon_wrap(
    f'<path d="M24 26 V70 H74" stroke="{TETH}" stroke-width="2" fill="none"/>'
    f'<path d="M28 60 C38 60 40 34 50 34 S62 58 72 40" stroke="{TEAL}" stroke-width="3" fill="none" stroke-linecap="round"/>', 'Read the impedance')
files['step-look'] = icon_wrap(
    f'<path d="M40 16 h16 v14 l6 10 h-28 l6 -10z" fill="{MINT}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    f'<path d="M48 40 v10" stroke="{TEAL}" stroke-width="3" opacity=".7"/>'
    f'<rect x="22" y="56" width="52" height="12" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    f'<circle cx="40" cy="62" r="2.2" fill="{TEAL}"/><circle cx="48" cy="62" r="2.2" fill="{TEAL}" opacity=".6"/><circle cx="56" cy="62" r="2.2" fill="{TEAL}" opacity=".35"/>', 'Look on a slide')

# ---- "the gap" comparison minis (240x120) ----
def gap_card(kind, label):
    return svg(240, 110, f'<rect width="240" height="110" rx="12" fill="#F6F7FA"/>' + trace(20, 14, 200, 80, kind) +
               text(20, 106, 'time →', 9), label)
files['gap-endpoint'] = gap_card('endpoint', 'Endpoint readout: one value at the end')
files['gap-realtime'] = gap_card('sigmoid', 'MemChip: continuous real-time membrane signal')
def bars_card(label):
    b = ''.join(f'<rect x="{40+i*42}" y="{94-h}" width="26" height="{h}" rx="4" fill="{c}"/>' for i, (h, c) in enumerate([(22, TAIL), (40, TAIL), (64, TAIL), (30, TAIL)]))
    return svg(240, 110, f'<rect width="240" height="110" rx="12" fill="#F6F7FA"/><path d="M20 14 V94 H220" stroke="{TETH}" stroke-width="1.2" fill="none"/>' + b + text(20, 106, 'separate assays', 9), label)
files['gap-bars'] = bars_card('Several separate assays, each a snapshot')

# ---- assay schematics (720x220): membrane -> add -> trace ----
def assay(left_extra, right_kind, title_l, title_m, title_r, label, gap=None, mid_extra=''):
    b = [f'<rect width="720" height="220" rx="18" fill="#F6F7FA"/>']
    b.append(bilayer(30, 200, 92, 14))
    b.append(left_extra)
    b.append(arrow(220, 120, 268))
    b.append(f'<g transform="translate(250 0)">{bilayer(30, 200, 92, 14, gap=gap)}{mid_extra}</g>')
    b.append(arrow(470, 120, 518))
    b.append(f'<rect x="530" y="52" width="164" height="120" rx="12" fill="#fff" stroke="{"#E7E6E3"}"/>')
    b.append(trace(546, 66, 132, 84, right_kind, marker=.42))
    b.append(text(115, 192, title_l, 11, INK, 'middle', 500))
    b.append(text(365, 192, title_m, 11, INK, 'middle', 500))
    b.append(text(612, 192, title_r, 11, INK, 'middle', 500))
    return svg(720, 220, ''.join(b), label)

files['assay-lnp'] = assay('', 'decay', 'endosomal membrane mimic', 'add LNPs, drop to pH 6.0', 'fusion: admittance drops',
    'Assay: endosomal membrane mimic, add lipid nanoparticles, read the membrane signal in real time',
    mid_extra=lnp(80, 50) + lnp(150, 42, 15) + lnp(118, 76, 13))
files['assay-amp'] = assay('', 'sigmoid', 'bacterial membrane mimic', 'add peptide', 'ion flow as admittance',
    'Assay: bacterial-like membrane, add antimicrobial peptide, follow membrane disruption', gap=(104, 128),
    mid_extra=peptide(116, 98, 90) + peptide(116, 120, 90) + peptide(60, 60, 10) + peptide(170, 56, -15))
files['assay-sensor'] = assay('', 'step', 'tethered bilayer', 'insert channel + analyte', 'admittance change',
    'Assay: tethered bilayer, insert channel or pore, detect analyte as an admittance change', gap=(96, 136),
    mid_extra=channel(116, 92, open_=True) + f'<circle cx="104" cy="74" r="4" fill="{INDIGO}"/><circle cx="128" cy="72" r="4" fill="{INDIGO}"/>')

# ---- chip + slide: one membrane, two readouts (720x260) ----
b = [f'<rect width="720" height="260" rx="18" fill="#F6F7FA"/>']
b.append(bilayer(260, 460, 40, 16))
b.append(text(360, 22, 'one membrane, same surface', 11, INK, 'middle', 500))
b.append(f'<path d="M300 112 C260 140 200 140 170 158" stroke="{TEAL}" stroke-width="2" stroke-dasharray="5 5" fill="none"/>')
b.append(f'<path d="M420 112 C460 140 520 140 550 158" stroke="{TEAL}" stroke-width="2" stroke-dasharray="5 5" fill="none"/>')
b.append(f'<rect x="60" y="160" width="220" height="80" rx="12" fill="#fff" stroke="#E7E6E3"/>' + trace(76, 172, 130, 56, 'sigmoid'))
b.append(text(228, 196, 'MemChip', 11, INK, 'middle', 700) + text(228, 212, 'impedance', 10, MUTED, 'middle'))
b.append(f'<rect x="440" y="160" width="220" height="80" rx="12" fill="#fff" stroke="#E7E6E3"/>')
b.append(f'<rect x="456" y="172" width="120" height="56" rx="6" fill="#16152a"/>')
import random
random.seed(4)
for _ in range(26):
    x = 462+random.random()*108; y = 178+random.random()*44; r = 1.2+random.random()*2.4
    b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{TEAL}" opacity="{.35+random.random()*.6:.2f}"/>')
b.append(text(616, 196, 'Slide', 11, INK, 'middle', 700) + text(616, 212, 'microscopy', 10, MUTED, 'middle'))
files['chip-slide'] = svg(720, 260, ''.join(b), 'One membrane, two readouts: MemChip gives an impedance trace, the surface-matched slide gives a microscopy image')

# ---- beta: three steps (720x150) ----
def beta_step(x, n, t, sub, icon):
    return (f'<circle cx="{x}" cy="56" r="38" fill="#fff" stroke="{MINT}" stroke-width="2"/>{icon}'
            + text(x, 118, f'{n}  {t}', 12, INK, 'middle', 700) + text(x, 136, sub, 10.5, MUTED, 'middle'))
ic1 = f'<rect x="102" y="40" width="36" height="28" rx="4" fill="none" stroke="{INK}" stroke-width="2"/><path d="M102 44 l18 13 l18 -13" stroke="{TEAL}" stroke-width="2" fill="none"/>'
ic2 = f'<rect x="340" y="42" width="40" height="28" rx="4" fill="{MINT}" stroke="{INK}" stroke-width="2"/><path d="M340 52 h40" stroke="{INK}" stroke-width="2"/><rect x="354" y="36" width="12" height="8" rx="2" fill="{TEAL}"/>'
ic3 = f'<path d="M580 72 V40 M580 72 H616" stroke="{TETH}" stroke-width="2"/><path d="M584 66 C592 66 594 46 602 46 S610 60 614 50" stroke="{TEAL}" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
b = [beta_step(120, '01', 'Request', 'tell us what you want to measure', ic1),
     arrow(170, 56, 300),
     beta_step(360, '02', 'Receive', 'trial chips, protocol, support', ic2),
     arrow(410, 56, 540),
     beta_step(600, '03', 'Measure + share', 'your data, your feedback', ic3)]
files['beta-steps'] = svg(720, 150, ''.join(b), 'Three steps: request, receive trial chips, measure and share feedback')

for k, v in files.items():
    open(os.path.join(OUT, k + '.svg'), 'w').write(v)
print('wrote', len(files), 'svgs')

# ---- anatomy (720x240), generic: electrode, tethers, bilayer ----
b = [f'<rect width="720" height="240" rx="18" fill="#F6F7FA"/>', bilayer(50, 390, 78, 26)]
def callout(xa, ya, y, t, sub):
    return (f'<path d="M{xa} {ya} H440 L460 {y} H478" stroke="{TEAL}" stroke-width="1.6" fill="none"/><circle cx="{xa}" cy="{ya}" r="3.2" fill="{TEAL}"/>'
            + text(488, y+4, t, 13, INK, 'start', 700) + text(488, y+21, sub, 11, MUTED))
b.append(callout(394, 78, 54, 'Lipid bilayer', 'your composition, mobile lipids'))
b.append(callout(338, 116, 120, 'Tethers', 'hold the membrane in place'))
b.append(callout(396, 127, 184, 'Support layer', 'proprietary architecture above an electrode'))
files2 = {'anatomy': svg(800, 240, ''.join(b), 'MemChip anatomy: a lipid bilayer held by tethers on a proprietary membrane surface above the electrode')}
for k, v in files2.items():
    open(os.path.join(OUT, k + '.svg'), 'w').write(v)
print('wrote anatomy')
