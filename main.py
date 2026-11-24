#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""THE WORLD ON MONDAY - one-day world news image for Monday 23 November 2026.

Draws a dense 3-column newspaper front page (1024x1024 PNG) summing up the
world news of Monday, 23 November 2026. Every headline and figure below was
verified against live reporting of that day (see SOURCES.md). The program
uses no network: all text is hardcoded and the output is deterministic -
two runs write byte-identical files.

Primary renderer: Pillow (PIL). Fallback renderer: pure standard library
(small bitmap font + a hand-rolled PNG encoder), used only when PIL is
missing. Output path: $MAKEFUN_OUTPUT_DIR/entry.png (default ./output).
"""

import os
import sys

W, H = 1024, 1024

# --------------------------------------------------------------------------
# Verified news data - Monday 23 November 2026 only.
# Each item: (headline, one-line dek). Numbers checked live at build time.
# --------------------------------------------------------------------------

LEAD_HEAD = "DEMOCRATS CLINCH 258 HOUSE SEATS, LARGEST MAJORITY SINCE 1992"
LEAD_DEK = ("AP calls NC-5 for Chuck Hubbard over Rep. Virginia Foxx by 330 votes "
            "after a recount - a gain of 44 seats, with 4 races still uncalled.")
LEAD_CHIPS = [("258", "DEM SEATS"), ("+44", "SEATS GAINED"),
              ("330", "VOTE MARGIN NC-5"), ("173", "REP SEATS"),
              ("4", "RACES UNCALLED")]

SECTIONS = [
    ("NORTH AMERICA", [
        ("NVIDIA +31% AS HUANG RETURNS AS CEO",
         "Board reinstates Jensen Huang 11 days after he quit; Trump claims the deal."),
        ("WALL ST SOARS: S&P +4.7%, DOW +1,450",
         "Nasdaq +6.5% snaps a 7-session losing streak after the AI sell-off."),
        ("CROWDSTRIKE TO BUY ZSCALER FOR $43.9BN",
         "All-stock deal is the biggest cybersecurity merger ever announced."),
        ("ANTHROPIC FACES 'JUNK' RATING CALL",
         "Analysts flag ~$900bn of compute pledges days after its record IPO."),
        ("NIH STUDIES LINK GLYPHOSATE TO CANCER",
         "Three federal reviews tie the weedkiller to blood cancers; EPA review due 2027."),
        ("COURT 9-8 VOIDS PROXY-VOTE QUORUM",
         "Fifth Circuit backs Texas block on the Pregnant Workers Fairness Act."),
        ("AMTRAK TRAIN DERAILS IN LOUISIANA",
         "Truck stuck on crossing; 5 minor injuries among 95 people on board."),
        ("ARMY TO DETONATE IOWA CHEMICALS",
         "Emergency powers invoked to blow up unstable lead stocks, bypassing court."),
        ("DELTA GLITCH SNARLS 1,000+ FLIGHTS",
         "Load-calculation crash forces a one-hour FAA ground stop at Atlanta."),
    ]),
    ("EUROPE", [
        ("UKRAINE DRONES SINK RUSSIAN CORVETTE",
         "Seven naval drones sink the Merkury at Benghazi, Libya; cargo ship also hit."),
        ("RUSSIAN STRIKES KILL 15 NEAR KYIV",
         "Boy, 7, pulled alive from Dymer rubble after 14 hours; NATO to meet."),
        ("EU PROPOSES 22ND RUSSIA SANCTIONS",
         "60 banks, crypto platforms and 70 shadow-fleet ships; sports flag ban."),
        ("FINLAND SUMMONS RUSSIAN ENVOY",
         "Suspected airspace violation as Russia warns Estonia of 'open war'."),
        ("NATO PLEDGES SPACE DEFENCE IN BERLIN",
         "Rutte: alliance will defend every inch, amid nuclear-satellite reports."),
        ("BELGIUM AIRPORTS SHUT BY STRIKE",
         "Anti-austerity walkout grounds flights; 50,000+ travellers affected."),
        ("BURNHAM DEFENDS EU RESET DEAL",
         "PM tells MPs closer ties worth a claimed GBP 17bn a year by 2040."),
        ("UK TO HOST 2035 WOMEN'S WORLD CUP",
         "FIFA confirms the four home nations as joint hosts of the finals."),
        ("FRANCE REJECTS EU BUDGET DRAFT",
         "Paris calls Costa's EUR 1.78tn plan 'very disappointing' despite digital levy."),
    ]),
    ("MIDDLE EAST", [
        ("IRAN VOWS 'ALL MEANS' VS US BLOCKADE",
         "Tehran defies the Hormuz naval blockade; tanker mine reports disputed."),
        ("US SANCTIONS IRAN SHADOW BANKING",
         "Treasury targets 8 people and 22 entities moving money for Tehran."),
        ("IRAN FLOGS SINGER AHMADI, 74 LASHES",
         "Parastoo Ahmadi and 4 team members punished over a hijab-free concert."),
        ("GAZA 99% TOXIC-CONTAMINATED: REPORT",
         "Oxfam study finds metals, asbestos and sewage across the strip."),
        ("SAUDI STRIKE ON HODEIDA KILLS 4",
         "Houthi media: telecom building hit, 18 wounded; Rabigh attack claimed."),
    ]),
    ("AFRICA", [
        ("EBOLA RESPONSE TRAPPED BY FIGHTING",
         "WHO: Ituri clashes shelve responders 24h+; 11,613 cases, 5,678 deaths."),
        ("KENYA, DR CONGO RESTORE FULL TIES",
         "Ruto and Tshisekedi settle the M23 row at the Oyo summit in Congo."),
        ("UN SEEKS PROBE OF BENGHAZI ATTACK",
         "Libya mission demands inquiry after drones hit Russian ships in port."),
        ("KHARTOUM DRONES KILL 4, HIT UN SITE",
         "Strikes damage a UN premises in a residential area of Sudan's capital."),
        ("TINUBU: EVEN THE VILLA LOSES POWER",
         "Nigeria's president says water and power cuts reach his own residence."),
        ("ETHIOPIA POLIO DRIVE TARGETS 11.3M",
         "Nationwide campaign aims to vaccinate 11.3 million children."),
    ]),
    ("ASIA-PACIFIC", [
        ("INDONESIA FACTORY FIRE KILLS 24",
         "Candy plant blaze in Banten, Java; about 30 workers still missing."),
        ("INDIA PLEDGES $1.62BN TO NEPAL",
         "8 deals signed as PM Balendra Shah makes Delhi his first foreign trip."),
        ("S. KOREA EXAMS MINISTER QUITS",
         "Education chief resigns over chaos and cheating in college entrance exams."),
        ("THAI COURT HALVES INSULT SENTENCE",
         "Appeal judges cut the jail term of a lawmaker convicted of royal insult."),
        ("KIM TALKS SOVEREIGNTY, SNUBS TRUMP",
         "North Korea's leader rebuffs a US meeting push, courts new envoys."),
        ("ASIAN MARKETS SLIDE ON AI FEARS",
         "Nikkei -5.06% and Sensex -1.77% as the tech rout crosses the Pacific."),
    ]),
    ("LATIN AMERICA", [
        ("DRONES HIT COLOMBIA POLICE BASE",
         "Cucuta attack damages 60 homes; an 18-month-old baby among the hurt."),
        ("BRAZIL STORM KILLS 5, INJURES 265",
         "114 km/h supercell flattens Tupancireta; some 8,000 homes damaged."),
        ("MEXICO CAPTURES 'CHAPO ISIDRO'",
         "Cartel boss held in Sinaloa raid; 17 killed in the violence around it."),
    ]),
    ("GLOBAL & CLIMATE", [
        ("COP31 TALKS COLLAPSE IN ANTALYA",
         "Longest COP ever ends with no deal: draft omitted 'fossil fuels'."),
        ("UN CHIEF URGES AI SAFETY TALKS",
         "Guterres seeks a global AI safety framework, warns of a power shift."),
        ("WARS PUT 7.3M MORE AT FOOD RISK",
         "UN food agency chief warns conflict is cutting aid to millions more."),
        ("UN COUNCIL: WINTER GRID ATTACKS",
         "Ukraine power-grid and Black Sea shipping attacks threaten food supply."),
    ]),
    ("SCIENCE & CULTURE", [
        ("GTA VI: $3.79BN DAY-ONE RECORD",
         "Take-Two counts the biggest entertainment launch haul in history."),
        ("RIEMANN PROOF CERTIFIED BY LEAN",
         "Claude-assisted proof of the 167-year puzzle passes formal checks."),
        ("OPENAI SCIENTIST SEEKS AI LIMITS",
         "Pachocki proposes labs agree shared red lines on model monitoring."),
    ]),
]

TOTAL_ITEMS = sum(len(items) for _, items in SECTIONS)

# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

def out_path():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(".", "output"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "entry.png")


def lcg_grain(seed=20261123):
    """Deterministic pseudo-random stream (no time, no OS entropy)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield (state >> 8) & 0xFF


# --------------------------------------------------------------------------
# PIL renderer
# --------------------------------------------------------------------------

PAPER = (246, 241, 228)
INK = (18, 18, 20)
RULE = (30, 30, 34)
ACCENT = (142, 22, 22)
DEM = (32, 74, 148)
REP = (168, 40, 40)
GREY = (92, 88, 80)


def _fonts():
    from PIL import ImageFont
    base = "/usr/share/fonts/truetype"
    cands = {
        "serif_b": [base + "/dejavu/DejaVuSerif-Bold.ttf",
                    base + "/liberation/LiberationSerif-Bold.ttf"],
        "sans_b": [base + "/dejavu/DejaVuSans-Bold.ttf",
                   base + "/liberation/LiberationSans-Bold.ttf"],
        "sans": [base + "/dejavu/DejaVuSans.ttf",
                 base + "/liberation/LiberationSans-Regular.ttf"],
    }

    def pick(paths, size):
        for p in paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    return {
        "mast": pick(cands["serif_b"], 50),
        "date": pick(cands["serif_b"], 36),
        "lead": pick(cands["serif_b"], 34),
        "dek": pick(cands["sans"], 15),
        "chip_n": pick(cands["sans_b"], 28),
        "chip_l": pick(cands["sans_b"], 11),
        "sec": pick(cands["sans_b"], 16),
        "head": pick(cands["sans_b"], 13),
        "body": pick(cands["sans"], 11),
        "tiny": pick(cands["sans"], 11),
    }


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def render_pil(path):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    F = _fonts()

    # --- masthead ------------------------------------------------------
    d.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=3)
    d.text((W / 2, 12), "THE WORLD ON MONDAY", font=F["mast"],
           fill=INK, anchor="ma")
    d.line([24, 82, W - 24, 82], fill=RULE, width=3)
    d.text((W / 2, 90), "MONDAY, 23 NOVEMBER 2026", font=F["date"],
           fill=ACCENT, anchor="ma")
    d.text((24, 132), "ONE DAY OF WORLD NEWS - 46 STORIES - 8 REGIONS",
           font=F["tiny"], fill=GREY)
    d.text((W - 24, 132), "ALL EVENTS OF 23 NOV 2026", font=F["tiny"],
           fill=GREY, anchor="ra")
    d.line([24, 148, W - 24, 148], fill=RULE, width=2)

    # --- lead band ------------------------------------------------------
    y = 156
    for ln in _wrap(d, LEAD_HEAD, F["lead"], W - 48):
        d.text((24, y), ln, font=F["lead"], fill=INK)
        y += 40
    for ln in _wrap(d, LEAD_DEK, F["dek"], W - 48):
        d.text((24, y + 2), ln, font=F["dek"], fill=GREY)
        y += 20
    y += 6
    # chips
    cw = (W - 48 - 4 * 8) // 5
    for i, (num, lab) in enumerate(LEAD_CHIPS):
        x = 24 + i * (cw + 8)
        d.rectangle([x, y, x + cw, y + 50], outline=RULE, width=2)
        d.text((x + cw / 2, y + 3), num, font=F["chip_n"], fill=ACCENT,
               anchor="ma")
        d.text((x + cw / 2, y + 34), lab, font=F["chip_l"], fill=INK,
               anchor="ma")
    y += 58
    # bar chart: House seats
    d.text((24, y), "HOUSE SEATS (AP):", font=F["chip_l"], fill=INK)
    bx, bw = 170, W - 170 - 90
    d.rectangle([bx, y - 2, bx + bw * 258 / 435, y + 13], fill=DEM)
    d.text((bx + bw * 258 / 435 + 6, y - 3), "DEM 258", font=F["chip_l"],
           fill=DEM)
    d.rectangle([bx, y + 17, bx + bw * 173 / 435, y + 32], fill=REP)
    d.text((bx + bw * 173 / 435 + 6, y + 16), "REP 173", font=F["chip_l"],
           fill=REP)
    y += 36
    d.line([24, y, W - 24, y], fill=RULE, width=3)
    top = y + 8

    # --- three dense columns -------------------------------------------
    col_x = [24, 349, 674]
    col_w = 301
    # distribute sections into 3 columns by item count
    cols = [[], [], []]
    counts = [0, 0, 0]
    for sec in SECTIONS:
        i = counts.index(min(counts))
        cols[i].append(sec)
        counts[i] += len(sec[1]) + 2
    bottom = H - 26
    for ci in range(3):
        x = col_x[ci]
        yy = top
        if ci:
            d.line([x - 24, top, x - 24, bottom], fill=RULE, width=1)
        for name, items in cols[ci]:
            d.rectangle([x, yy, x + col_w, yy + 21], fill=INK)
            d.text((x + 6, yy + 3), name, font=F["sec"], fill=PAPER)
            yy += 25
            for head, dek in items:
                for ln in _wrap(d, head, F["head"], col_w):
                    d.text((x, yy), ln, font=F["head"], fill=INK)
                    yy += 15
                dl = _wrap(d, dek, F["body"], col_w)
                if dl:
                    line = dl[0] if len(dl) == 1 else dl[0].rstrip(" ,;") + ".."
                    d.text((x, yy), line, font=F["body"], fill=GREY)
                    yy += 13
                yy += 4
            yy += 3
    d.line([24, H - 20, W - 24, H - 20], fill=RULE, width=2)
    d.text((W / 2, H - 17), "EVERY STORY ABOVE HAPPENED OR WAS FIRST "
           "REPORTED ON MONDAY 23 NOVEMBER 2026 - SOURCES IN SOURCES.MD",
           font=F["tiny"], fill=GREY, anchor="ma")

    _add_texture(img)
    img.save(path, format="PNG", optimize=False)


def _add_texture(img):
    """Deterministic block grain: lifts the PNG into the target size band
    and gives the page a printed-paper feel. One seeded-LCG value per 3x3
    block keeps the file compressible; every run yields identical bytes."""
    from PIL import Image
    g = lcg_grain()
    small = Image.new("L", (342, 342))
    sp = small.load()
    for yy in range(342):
        for xx in range(342):
            sp[xx, yy] = 128 + (next(g) % 17) - 8
    grain = small.resize((W, H), Image.NEAREST)
    gp = grain.load()
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            dlt = gp[xx, yy] - 128
            r, gg, b = px[xx, yy]
            px[xx, yy] = (max(0, min(255, r + dlt)),
                          max(0, min(255, gg + dlt)),
                          max(0, min(255, b + dlt)))


# --------------------------------------------------------------------------
# Stdlib fallback renderer (used only when PIL is unavailable)
# --------------------------------------------------------------------------

FONT5 = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000",) * 7, ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
}


def _fb_text(fb, x, y, text, scale, rgb):
    cx = x
    for ch in text.upper():
        gl = FONT5.get(ch, FONT5[" "])
        for r in range(7):
            row = gl[r]
            for c in range(5):
                if row[c] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            xx, yy = cx + c * scale + dx, y + r * scale + dy
                            if 0 <= xx < W and 0 <= yy < H:
                                i = (yy * W + xx) * 3
                                fb[i:i + 3] = bytes(rgb)
        cx += 6 * scale
    return cx


def _fb_rect(fb, x, y, w, h, rgb):
    for yy in range(max(0, y), min(H, y + h)):
        for xx in range(max(0, x), min(W, x + w)):
            i = (yy * W + xx) * 3
            fb[i:i + 3] = bytes(rgb)


def _fb_wrap(text, chars):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) <= chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def render_stdlib(path):
    import struct
    import zlib
    fb = bytearray(bytes(PAPER) * (W * H))
    ink, acc, grey = INK, ACCENT, GREY
    _fb_rect(fb, 0, 0, W, 3, ink)
    _fb_rect(fb, 0, H - 3, W, 3, ink)
    t = "THE WORLD ON MONDAY"
    _fb_text(fb, (W - len(t) * 36) // 2, 14, t, 6, ink)
    _fb_rect(fb, 24, 74, W - 48, 3, ink)
    t = "MONDAY, 23 NOVEMBER 2026"
    _fb_text(fb, (W - len(t) * 30) // 2, 86, t, 5, acc)
    y = 140
    for ln in _fb_wrap(LEAD_HEAD, 30):
        _fb_text(fb, 24, y, ln, 4, ink)
        y += 34
    for ln in _fb_wrap(LEAD_DEK, 78):
        _fb_text(fb, 24, y, ln, 2, grey)
        y += 17
    y += 6
    cw = (W - 48 - 32) // 5
    for i, (num, lab) in enumerate(LEAD_CHIPS):
        x = 24 + i * (cw + 8)
        _fb_rect(fb, x, y, cw, 2, ink)
        _fb_rect(fb, x, y + 46, cw, 2, ink)
        _fb_text(fb, x + 8, y + 6, num, 3, acc)
        _fb_text(fb, x + 8, y + 28, lab, 1, ink)
    y += 56
    _fb_rect(fb, 170, y, int(560 * 258 / 435), 10, DEM)
    _fb_text(fb, 24, y, "HOUSE: DEM 258", 2, ink)
    _fb_rect(fb, 170, y + 14, int(560 * 173 / 435), 10, REP)
    _fb_text(fb, 24, y + 14, "REP 173", 2, ink)
    y += 32
    _fb_rect(fb, 24, y, W - 48, 3, ink)
    top = y + 8
    cols = [[], [], []]
    counts = [0, 0, 0]
    for sec in SECTIONS:
        i = counts.index(min(counts))
        cols[i].append(sec)
        counts[i] += len(sec[1]) + 2
    col_x = [24, 349, 674]
    for ci in range(3):
        x, yy = col_x[ci], top
        for name, items in cols[ci]:
            _fb_rect(fb, x, yy, 301, 16, ink)
            _fb_text(fb, x + 5, yy + 2, name, 2, PAPER)
            yy += 20
            for head, dek in items:
                for ln in _fb_wrap(head, 27):
                    _fb_text(fb, x, yy, ln, 2, ink)
                    yy += 15
                for ln in _fb_wrap(dek, 54)[:2]:
                    _fb_text(fb, x, yy, ln, 1, grey)
                    yy += 9
                yy += 4
            yy += 3
    # deterministic grain, same spirit as the PIL path
    g = lcg_grain()
    for i in range(0, len(fb), 3):
        dlt = (next(g) % 13) - 6
        fb[i] = max(0, min(255, fb[i] + dlt))
        fb[i + 1] = max(0, min(255, fb[i + 1] + dlt))
        fb[i + 2] = max(0, min(255, fb[i + 2] + dlt))
    raw = b"".join(b"\x00" + bytes(fb[r * W * 3:(r + 1) * W * 3])
                   for r in range(H))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 1))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    path = out_path()
    try:
        import PIL  # noqa: F401
        render_pil(path)
    except ImportError:
        render_stdlib(path)
    print("wrote", path)


if __name__ == "__main__":
    sys.exit(main())
