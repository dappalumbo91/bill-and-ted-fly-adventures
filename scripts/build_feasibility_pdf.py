#!/usr/bin/env python3
"""Rebuild the feasibility plan PDF with readable FSOT math and live pack status.

Uses Windows Times New Roman so Greek (pi, phi, gamma, alpha, tau) actually
renders. Original Gemini export is left beside this file as .gemini-export.pdf.
"""
from __future__ import annotations

import runio
runio.install()

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Bio-Neuromorphic Connectome Expansion Feasibility.pdf"

NAVY = colors.HexColor("#1b365d")
TEAL = colors.HexColor("#0e6b6b")
RULE = colors.HexColor("#c5cdd6")
HEAD_BG = colors.HexColor("#e8eef4")
LIVE = colors.HexColor("#e8f5e9")
PAUSE = colors.HexColor("#fff8e1")
MATH_BG = colors.HexColor("#f4f7fb")

USABLE = letter[0] - 1.4 * inch
FONT = {"body": "Times-Roman", "bold": "Times-Bold", "italic": "Times-Italic", "bi": "Times-BoldItalic"}


def register_fonts() -> None:
    """Prefer a Times file when one is installed. Otherwise use the built-in face."""
    candidates = []
    import os
    if os.environ.get("FONT_DIR"):
        candidates.append(Path(os.environ["FONT_DIR"]))
    candidates.append(Path(r"C:\Windows\Fonts"))
    candidates.append(Path("/usr/share/fonts/truetype/liberation"))
    candidates.append(Path("/usr/share/fonts/truetype/dejavu"))
    names = (
        ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"),
        ("LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf", "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf"),
        ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf", "DejaVuSerif-BoldItalic.ttf"),
    )
    for folder in candidates:
        for quartet in names:
            paths = [folder / name for name in quartet]
            if all(p.is_file() for p in paths):
                pdfmetrics.registerFont(TTFont("TNR", str(paths[0])))
                pdfmetrics.registerFont(TTFont("TNR-B", str(paths[1])))
                pdfmetrics.registerFont(TTFont("TNR-I", str(paths[2])))
                pdfmetrics.registerFont(TTFont("TNR-BI", str(paths[3])))
                pdfmetrics.registerFontFamily(
                    "TNR", normal="TNR", bold="TNR-B", italic="TNR-I", boldItalic="TNR-BI"
                )
                FONT["body"] = "TNR"
                FONT["bold"] = "TNR-B"
                FONT["italic"] = "TNR-I"
                FONT["bi"] = "TNR-BI"
                return


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontName=FONT["bold"], fontSize=16,
            leading=20, textColor=NAVY, spaceAfter=6, alignment=TA_LEFT,
        ),
        "sub": ParagraphStyle(
            "S", parent=base["Normal"], fontName=FONT["italic"], fontSize=9,
            leading=12, textColor=TEAL, spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName=FONT["bold"], fontSize=12,
            leading=15, textColor=NAVY, spaceBefore=11, spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName=FONT["bold"], fontSize=10.5,
            leading=13, textColor=TEAL, spaceBefore=8, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName=FONT["body"], fontSize=9.5,
            leading=12.5, spaceAfter=5,
        ),
        "cell": ParagraphStyle(
            "C", parent=base["Normal"], fontName=FONT["body"], fontSize=8,
            leading=10.5,
        ),
        "cellb": ParagraphStyle(
            "CB", parent=base["Normal"], fontName=FONT["bold"], fontSize=8,
            leading=10.5,
        ),
        "math": ParagraphStyle(
            "M", parent=base["Normal"], fontName="TNR-I", fontSize=9.5,
            leading=13, textColor=NAVY, spaceAfter=2,
        ),
        "foot": ParagraphStyle(
            "F", parent=base["Normal"], fontName="TNR-I", fontSize=8,
            leading=10, textColor=colors.HexColor("#555555"),
        ),
    }


def P(text, st):
    return Paragraph(text, st)


def tbl(rows, widths, header=True, fill=HEAD_BG):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
    ]
    if header:
        cmds.append(("BACKGROUND", (0, 0), (-1, 0), fill))
    t.setStyle(TableStyle(cmds))
    return t


def mathbox(lines, st):
    rows = [[P(line, st["math"])] for line in lines]
    t = Table(rows, colWidths=[USABLE])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MATH_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 1),
        ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.setFont("TNR-B", 8)
    canvas.drawString(0.7 * inch, letter[1] - 0.42 * inch, "FSOT fly program — feasibility plan")
    canvas.setFont("TNR", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(
        letter[0] - 0.7 * inch, letter[1] - 0.42 * inch,
        "pin D1D38A  ·  0 free parameters",
    )
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.6)
    canvas.line(0.7 * inch, letter[1] - 0.50 * inch, letter[0] - 0.7 * inch, letter[1] - 0.50 * inch)
    canvas.setFont(FONT["italic"], 8)
    canvas.drawString(
        0.7 * inch, 0.38 * inch,
        "Updated 2026-09-17  ·  original Gemini export kept as .gemini-export.pdf",
    )
    canvas.drawRightString(letter[0] - 0.7 * inch, 0.38 * inch, str(doc.page))
    canvas.restoreState()


def build():
    register_fonts()
    st = styles()
    c = st["cell"]
    b = st["cellb"]
    story = []

    story.append(P("Bio-Neuromorphic Connectome Expansion Feasibility", st["title"]))
    story.append(P(
        "FSOT-stamped plan for the fly program in <i>fsot fly nuron net</i>. "
        "Original Gemini conversation (2026-09-15) treated the mathematics as out of scope. "
        "This revision puts the formulas in. Law "
        "<i>S = K(T<sub>1</sub> + T<sub>2</sub> + T<sub>3</sub>)</i>. Residual "
        "<i>r = 1 + |S| · P<sub>NEW</sub></i>. Pin D1D38A. 0 free parameters.",
        st["sub"],
    ))

    # ── 0 bookmark ────────────────────────────────────────────────────────
    story.append(P("0. Bookmark — where we left the other work", st["h1"]))
    story.append(P(
        "Before this fly pack was split out, FSOT-Genetics finished the plant "
        "<b>information graph</b> (not a connectome) and pushed GitHub "
        "<b>61872b4</b> (2026-09-17). Circle back there after this plan is locked. "
        "Do not drop that panel.",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Item</b>", b), P("<b>Status</b>", b), P("<b>Where</b>", b)],
            [P("Arabidopsis IntAct PPI hops", c),
             P("Done. 8,329 proteins, 39,664 physical edges. Photoreceptor hop-1 → PIF3 (light_tf = 1.00). Calvin hop-2 stays on psbA. Auxin hop-2 → TIR1. SLAC1 almost unlit (~0.001); kinase→channel is often phosphorylation, not a binary IntAct edge.", c),
             P("FSOT-Genetics data/plant_signal_boot.json", c)],
            [P("Signaling product Cα", c),
             P("Done. PHYB / CRY1 / OST1 / ABI1 / PIN1 / TIR1 product. PIF3 identity 0.69 (≥ 1/φ). PHOT1 no_measured_map (no homolog structure; not bulk MDS).", c),
             P("data/plant_signal_product.json", c)],
            [P("Crop homologs rice / maize / soy / wheat", c),
             P("Done. 24/24 folded. GitHub bc22797 then 61872b4.", c),
             P("data/plant_homolog.json", c)],
            [P("Gauntlet Lean / Coq / Isabelle / F* / SMT / Rust / TLA+", c),
             P("Re-stamped after plant-signal + hemibrain. overall_ok = true, 10 layers.", c),
             P("python verification/run_cross_proof.py", c)],
        ],
        [1.55 * inch, 3.7 * inch, 1.85 * inch],
        fill=PAUSE,
    ))

    # ── 1 plan ────────────────────────────────────────────────────────────
    story.append(P("1. The plan (from the original feasibility conversation)", st["h1"]))
    story.append(P(
        "Take a <b>measured</b> fly wiring diagram as the sensory–motor substrate. "
        "Do not train a giant weight matrix to invent synapses. Expand by grafting "
        "higher-order architectures at <b>interface hubs</b> (gating, action selection, "
        "sparse memory, neuromodulatory gain). Genetics (codon → trit → protein) "
        "anchors which cells can carry which residual job. Same scalar law on every organism.",
        st["body"],
    ))
    story.append(P(
        "Gemini called this architecturally feasible and then named four mammalian/avian "
        "hubs, a Hodgkin–Huxley circuit analog, and a species ladder (worm → fly → rodent "
        "MICrONS → human). The missing piece in that export was the math. FSOT already "
        "supplies the operators. The fly graph already supplies some analogs. Splicing a "
        "human thalamus onto FlyWire without a measured interface is still invention.",
        st["body"],
    ))

    # ── 2 math ────────────────────────────────────────────────────────────
    story.append(P("2. FSOT mathematics on this fly program", st["h1"]))

    story.append(P("2.1 Seeds (the only constants)", st["h2"]))
    story.append(P(
        "Every coefficient reduces to a closed form in {π, e, φ, γ}. "
        "Nothing on this pack is a fitted weight.",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Symbol</b>", b), P("<b>Closed form</b>", b), P("<b>Pin value</b>", b), P("<b>Role here</b>", b)],
            [P("π", c), P("circle constant", c), P("3.141592653589793", c), P("geometry, pair env, hop leftover via φ", c)],
            [P("e", c), P("natural base", c), P("2.718281828459045", c), P("pair base / elec; P<sub>NEW</sub> numerator", c)],
            [P("φ", c), P("(1 + √5) / 2", c), P("1.618033988749895", c), P("pair geom; active cut 1/φ; leftover φ<sup>5</sup>", c)],
            [P("γ", c), P("Euler–Mascheroni", c), P("0.577215664901533", c), P("P<sub>NEW</sub> = (γ/e) √2", c)],
            [P("P<sub>NEW</sub>", c), P("(γ / e) √2", c), P("≈ 0.30033", c), P("residual scale on every hop", c)],
            [P("K", c), P("φ · (γ/e) · √2 / ln(π) · 0.99", c), P("pin row", c), P("scalar prefactor; 0.99 is in the pin, not a fit", c)],
        ],
        [0.85 * inch, 2.05 * inch, 1.55 * inch, 2.65 * inch],
    ))

    story.append(P("2.2 Scalar law", st["h2"]))
    story.append(mathbox([
        "<b>S = K (T<sub>1</sub> + T<sub>2</sub> + T<sub>3</sub>)</b>",
        "T<sub>1</sub> observer-modulated base. Backbone geometry: observer <b>off</b>. Chemical links: observer <b>on</b>.",
        "T<sub>1</sub> = base · (1 + P<sub>NEW</sub> ln(D<sub>eff</sub> / 25)). If observed: multiply by exp(C<sub>FACTOR</sub> P<sub>VAR</sub>) cos(δψ + P<sub>VAR</sub>).",
        "T<sub>2</sub> = scale · amplitude + trend_bias (pin defaults).",
        "T<sub>3</sub> = valve · acoustic · phase, with chaos (D<sub>eff</sub> − 25)/25, poof/suction, acoustic δθ.",
        "D<sub>eff</sub> is a <b>named pin row</b>, not a fitted dimension.",
    ], st))
    story.append(Spacer(1, 4))
    story.append(P(
        "Code twin: <font face='Courier'>scripts/full_scalar_law.py</font> matches "
        "<font face='Courier'>vendor/fsot_compute.py</font> (authority D1D38A). "
        "Lean: <font face='Courier'>lean/ChemLink.lean</font>, "
        "<font face='Courier'>lean/Observer.lean</font> (backbone unobserved), "
        "<font face='Courier'>lean/SeedsReal.lean</font> (residual ≥ 1).",
        st["body"],
    ))

    story.append(P("2.3 Residual hop (this is the fly “net”)", st["h2"]))
    story.append(mathbox([
        "<b>r = 1 + |S| · P<sub>NEW</sub></b>  On Biochemistry, live <b>r ≈ 1.091959</b>.",
        "Each hop: <b>a ← r W a</b>, then <b>a ← a / ||a||<sub>∞</sub></b>.",
        "W<sub>ij</sub> = measured synapse count. GABA outgoing is inhibitory <b>when annotated</b>. Unsigned residual otherwise.",
        "Hop leftover = φ<sup>5</sup>. Active if amplitude &gt; 1/φ. Overlay cut = observer-max / φ.",
        "Amplitude rescale to observer-max after the cut. This is <b>not</b> backprop.",
    ], st))
    story.append(Spacer(1, 4))
    story.append(P(
        "Replacing W with trained weights exits the product. Gemini’s “synthetic gating "
        "matrices” and “STDP across the whole graph” are not this hop. The measured edge "
        "list stays the edge list.",
        st["body"],
    ))

    story.append(P("2.4 Chem-link D<sub>eff</sub> (Lean)", st["h2"]))
    story.append(tbl(
        [
            [P("<b>Link</b>", b), P("<b>Domain</b>", b), P("<b>D<sub>eff</sub></b>", b), P("<b>Observer</b>", b)],
            [P("backbone", c), P("Physical_Chemistry", c), P("8", c), P("off", c)],
            [P("disulfide", c), P("Atomic_Physics", c), P("7", c), P("on", c)],
            [P("salt bridge", c), P("Electromagnetism", c), P("9", c), P("on", c)],
            [P("hydrophobic pack", c), P("Condensed_Matter", c), P("14", c), P("on", c)],
            [P("H-bond secondary", c), P("Chemistry", c), P("8", c), P("on", c)],
            [P("molecular sidechain", c), P("Molecular_Chemistry", c), P("9", c), P("on", c)],
            [P("tertiary biochem", c), P("Biochemistry", c), P("13", c), P("on (hops use this r)", c)],
        ],
        [1.55 * inch, 2.15 * inch, 1.1 * inch, 2.3 * inch],
    ))

    story.append(P("2.5 Trinary genetics (64 codons → 20 amino-acid opcodes)", st["h2"]))
    story.append(P(
        "codon → primary/secondary trits in {−1, 0, +1} → amino acid → 7-trit word "
        "(c, p, v, aromatic, branch, hetero, detail). F01 (c, p, v) collides; the expanded "
        "word is <b>20/20 unique</b>. Pair weight on a residue pair at distance d:",
        st["body"],
    ))
    story.append(mathbox([
        "geom = φ · d<sup>−1/π</sup>",
        "base = τ<sub>i</sub> τ<sub>j</sub> e + (1 − |τ<sub>i</sub> τ<sub>j</sub>|) π",
        "elec = − q<sub>i</sub> q<sub>j</sub> e",
        "env = d / (d + π e)",
        "w = geom · (base + 0.15 elec) · (0.35 + 0.65 env)",
        "Check: <b>w(F, W, d = 8) = 1.670052</b>. Code: scripts/trinary_syntax.py. Maps: formulas/.",
    ], st))
    story.append(Spacer(1, 4))
    story.append(P(
        "A fly protein sequence is a string of these opcodes. Genes sit on hop jobs "
        "(MAP.md). They do not replace synapses.",
        st["body"],
    ))

    story.append(P("2.6 Product Cα (proteins that sit on the graph)", st["h2"]))
    story.append(mathbox([
        "Product = measured homolog template + residual packing. Same-data freeze: <b>0.13 Å</b> vs AlphaFold <b>0.47 Å</b> (n = 10).",
        "Close-homolog identity ≥ 1/φ. Leftover coverage floor 1/φ<sup>2</sup>. PRODUCT_IDENTITY_CAP = 1.0.",
        "No homolog → <b>no_measured_map</b> (Rg + secondary only). Not a 13 Å MDS brain. Not bulk.",
    ], st))

    story.append(P("2.7 What a hop number is (not RMSD)", st["h2"]))
    story.append(P(
        "Seed a measured sensory class. After two residual hops, does vnc_motor / descending light? "
        "Independent sexes, same split:",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Seed</b>", b), P("<b>Male CNS hop-2 vnc_motor</b>", b), P("<b>BANC hop-2 vnc_motor</b>", b)],
            [P("VNC sensory", c), P("<b>10.74</b>", c), P("<b>10.16</b>", c)],
            [P("Johnston organ", c), P("<b>7.77</b>", c), P("<b>6.64</b>", c)],
            [P("olfactory", c), P("0.001", c), P("0.0008", c)],
        ],
        [2.2 * inch, 2.5 * inch, 2.4 * inch],
        fill=LIVE,
    ))
    story.append(P(
        "JO hop-1 peaks DNg29 (male and BANC). Olfactory stays at antennal-lobe LNs. "
        "Larva: mechanosensory hop-2 DN-VNC 16.6 vs olfactory 0.43. GABA is the measured "
        "inhibitory transmitter, not a claimed thought.",
        st["body"],
    ))

    # ── 3 Gemini hurdles → FSOT ───────────────────────────────────────────
    story.append(P("3. Gemini’s three hurdles, answered with FSOT operators", st["h1"]))
    story.append(P(
        "The original export listed three engineering hurdles and left the math out. "
        "Here is the operator that already exists versus what would still be invention.",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Gemini hurdle</b>", b), P("<b>FSOT operator already running</b>", b), P("<b>Still invention if you…</b>", b)],
            [P("Neurotransmitter &amp; signal diversity (need gating matrices, not just wires)", c),
             P("W = synapse count. Sign from annotated NT only. GABA inhibitory on Male/BANC. Residual r is the graph-wide gain. DA / 5HT / octopamine only where the dump annotates them.", c),
             P("Invent octopamine rewires or dual-sign edges without annotation. Fitness-hack aggression off.", c)],
            [P("Plasticity alignment (STDP / whole-graph backprop)", c),
             P("Residual hops on frozen measured W. Overlay cut observer-max / φ. Active threshold 1/φ. Not STDP. Not a trained net.", c),
             P("Replace W with trained weights and still call it the FSOT product.", c)],
            [P("Dimensionality matching (need a thalamus-like bottleneck)", c),
             P("Overlay cut is the gate. DNg29 is the measured descending bottleneck on JO. CX / EB / FB types exist on FlyWire — do not call CX a thalamus.", c),
             P("Graft a human thalamus or 6-layer cortical column onto FlyWire without a measured interface graph.", c)],
        ],
        [1.7 * inch, 2.85 * inch, 2.55 * inch],
    ))

    # ── 4 systems ─────────────────────────────────────────────────────────
    story.append(P("4. Systems that must be connected", st["h1"]))
    story.append(P(
        "The original plan named fly wiring, worm, a third mapped animal, plants, "
        "human/Allen, genetics, and higher-order brain hubs. Status on 2026-09-17:",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>System</b>", b), P("<b>Role in the plan</b>", b), P("<b>Now</b>", b)],
            [P("FlyWire FAFB / Codex", c), P("Adult brain graph + types", c),
             P("LIVE in pack. Inventory 139,248. Codex page OK (CSV needs token).", c)],
            [P("Male CNS v1.0", c), P("Brain+VNC walking substrate", c),
             P("LIVE. 165,122 neurons, 25.6 M edges, 22,055 GABA. Feathers match frozen boot.", c)],
            [P("BANC v888", c), P("Female whole-animal, independent sex", c),
             P("LIVE hops in data/. Same JO vs olfactory split.", c)],
            [P("Larva", c), P("Developmental analog of DNg", c),
             P("LIVE hop JSON. Mechano DN-VNC 16.6 vs olfactory 0.43.", c)],
            [P("Janelia neuPrint hemibrain", c), P("Independent fly EM graph", c),
             P("LIVE hops. Typed 22,704 / 3.44 M edges. JO hop-2 descending 2.68 (Giant Fiber); olfactory 0.072 (AL LN). No VNC; DNg29 absent; unsigned (no predictedNt).", c)],
            [P("C. elegans (both sexes)", c), P("Foundational sensorimotor", c),
             P("LIVE in Genetics + worm JSON copied here. Male sex circuit lights.", c)],
            [P("Ciona / Platynereis", c), P("Other measured whole-animals", c),
             P("LIVE in Genetics. NT unsigned — do not invent GABA.", c)],
            [P("Genes on cells", c), P("nompC / iav / nan / Gad1 sit on hop jobs", c),
             P("LIVE UniProt names match. Ensembl nompC = FBgn. No Fly Cell Atlas bodyId invent.", c)],
            [P("Homologs bee / mosquito / beetle", c), P("Same proteins, no invented synapses", c),
             P("26 measured, 1 true miss (mec-4 Anopheles) → analog nompC.", c)],
            [P("Plant PPI / product", c), P("Information graph, not connectome", c),
             P("Recorded at 61872b4. Hemibrain hops done; gauntlet re-stamp is the plant-panel next.", c)],
            [P("Allen Brain Atlas", c), P("Human/mouse expression lock", c),
             P("API up; sample is developing mouse. Not fly synapses. CAVE (Allen software) serves FlyWire.", c)],
            [P("FSOT-2.1-Neural", c), P("Allen wet-lab / neural monorepo", c),
             P("GitHub live. Do not mix its 0.005% mouse claims with fly hop mass.", c)],
            [P("FSOT-2.1-Lean + gauntlet", c), P("Formal stamp", c),
             P("Genetics gauntlet overall_ok. This pack copies Lean chem-link / residual lemmas.", c)],
            [P("fsot-neuron-zig", c), P("Bare-metal pair geometry", c),
             P("Zig sources copied. GitHub live.", c)],
            [P("FSOT-Chua-Circuit", c), P("RLC circuit sibling, same pin", c),
             P("Reference only. HH analog in §6 uses residual r + D<sub>eff</sub> — not a new circuit theory.", c)],
        ],
        [1.6 * inch, 2.15 * inch, 3.35 * inch],
        fill=LIVE,
    ))

    # ── 5 hubs ────────────────────────────────────────────────────────────
    story.append(P("5. Four inter-system hubs — original plan, FSOT operators, fly analog", st["h1"]))
    story.append(P(
        "Gemini named four mammalian/avian hubs to splice onto a fly substrate, plus corvid NCL "
        "as a non-laminar alternative. FSOT already supplies the <b>operators</b>. The fly graph "
        "already supplies some <b>analogs</b>. A hub without a measured interface is still invention.",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Hub (plan)</b>", b), P("<b>CS translation</b>", b),
             P("<b>FSOT operator already in use</b>", b), P("<b>Fly measured analog</b>", b)],
            [P("Thalamocortical loop (gating / bus)", c),
             P("Packet switching, attention weights", c),
             P("Overlay cut = observer-max / φ; residual rescale each hop", c),
             P("Descending bottleneck DNg29 (JO hop-1). CX / EB / FB types on FlyWire. Do not call CX a thalamus.", c)],
            [P("CSTC / basal ganglia (Go / No-Go)", c),
             P("Thread lock, priority interrupt", c),
             P("Unsigned residual unless NT annotated; GABA edges inhibitory", c),
             P("Gad1 on GABAergic cells. Octopamine aggression is not a free rewire — need measured NT, not a fitness hack.", c)],
            [P("Entorhinal–hippocampal (sparse index)", c),
             P("Auto-associative memory, compression", c),
             P("Leftover coverage 1/φ<sup>2</sup>; close-homolog 1/φ on proteins", c),
             P("Mushroom-body Kenyon cells (FlyWire types). Pattern separation is a hop question on that subgraph, not a new MDS brain.", c)],
            [P("ARAS / neuromodulatory gain", c),
             P("Global voltage / learning-rate schedule", c),
             P("r = 1 + |S| · P<sub>NEW</sub> is already a graph-wide scalar", c),
             P("Biochemistry residual on every hop. DA / 5HT / octopamine only where the dump annotates them.", c)],
            [P("Avian NCL / crow (non-laminar exec)", c),
             P("Dense nuclear graph, working memory", c),
             P("Same residual law; no new operator required", c),
             P("No measured corvid connectome in this pack. Do not invent one. Fly analog is CX nuclear clusters, still not a crow brain.", c)],
        ],
        [1.55 * inch, 1.5 * inch, 2.0 * inch, 2.05 * inch],
    ))

    # ── 6 circuit ─────────────────────────────────────────────────────────
    story.append(P("6. Circuit view (Hodgkin–Huxley analog) under FSOT", st["h1"]))
    story.append(P(
        "The original plan’s car/circuit table stands: axons are wires, membrane is capacitance, "
        "channels are variable R, synapses are relays. FSOT does not replace HH; it supplies the "
        "<b>interface residual</b> and the <b>domain D<sub>eff</sub></b> when you treat a connection "
        "as chemistry (salt bridge, H-bond) versus geometry (backbone). Sibling lab: "
        "FSOT-Chua-Circuit (RLC array, same pin).",
        st["body"],
    ))
    story.append(tbl(
        [
            [P("<b>Circuit part</b>", b), P("<b>Biology</b>", b), P("<b>FSOT handle</b>", b)],
            [P("Wire", c), P("Axon / dendrite", c), P("Measured edge in W; do not invent", c)],
            [P("Resistor / transistor", c), P("Ion channel", c),
             P("Protein product Cα when homolog exists (nompC, iav, nan)", c)],
            [P("Relay", c), P("Synapse + NT", c),
             P("Weight = synapse count; sign from annotated NT only", c)],
            [P("Regulator / gain", c), P("Pumps, neuromodulators", c),
             P("Residual r; observer on/off by chem-link", c)],
            [P("Fuse / mute path", c), P("Hyperpolarization / GABA", c),
             P("Inhibitory GABA edges already in Male/BANC boots", c)],
        ],
        [1.6 * inch, 2.2 * inch, 3.3 * inch],
    ))

    # ── 7 genetics ────────────────────────────────────────────────────────
    story.append(P("7. Genetics hooked to the hop jobs (live)", st["h1"]))
    story.append(tbl(
        [
            [P("<b>Gene</b>", b), P("<b>UniProt</b>", b), P("<b>Template</b>", b),
             P("<b>Sits on</b>", b), P("<b>Hop seed</b>", b)],
            [P("nompC", c), P("Q7KIQ2", c), P("5VKQ", c), P("mechano / JO TRPN", c), P("JO", c)],
            [P("iav", c), P("Q9W3W0", c), P("9NVP", c), P("JO TRPV", c), P("JO", c)],
            [P("nan", c), P("Q9VUD5", c), P("9NVN", c), P("JO TRPV", c), P("JO", c)],
            [P("Gad1", c), P("P20228", c), P("2OKJ", c), P("GABA synthesis", c), P("VNC sensory / GABA cells", c)],
            [P("ChAT", c), P("P07668", c), P("2FY4", c), P("ACh synthesis (id 0.53 &lt; 1/φ)", c), P("vnc_sensory (excitatory default)", c)],
            [P("VGlut", c), P("Q9VQC0", c), P("7T3O", c), P("glutamatergic NMJ", c), P("vnc_sensory → vnc_motor", c)],
            [P("Mhc", c), P("P05661", c), P("5W1A", c), P("muscle myosin", c), P("not a CNS cell", c)],
        ],
        [0.95 * inch, 1.05 * inch, 0.9 * inch, 2.15 * inch, 2.05 * inch],
        fill=LIVE,
    ))
    story.append(P(
        "Live UniProt gene names match. Analog: mec-4 Anopheles has no 1:1; residual job on this "
        "graph is nompC, not a random ppk. Do not invent a Fly Cell Atlas bodyId join. "
        "Kenyon hops: KC stays in MB (hop-2 kenyon 35.1, descending 0.003); leftover hub is APL, not a thought.",
        st["body"],
    ))

    # ── 8 APIs ────────────────────────────────────────────────────────────
    story.append(P("8. Live APIs (ran 2026-09-17, fail = 0)", st["h1"]))
    story.append(P(
        "<font face='Courier'>python scripts/live_verify.py</font> — UniProt nompC, Ensembl nompC, "
        "neuPrint hemibrain v1.2.1, Codex FAFB page, GitHub FSOT-Genetics / 2.1-Lean / 2.1-Neural / "
        "fsot-neuron-zig, Allen Brain Atlas (up; developing mouse). Codex CSV dumps need an api_token. "
        "Allen is not the fly connectome.",
        st["body"],
    ))

    # ── 9–10 kept together so the closer is not an orphan page ────────────
    closer = []
    closer.append(P("9. What this pack will not do", st["h1"]))
    closer.append(ListFlowable(
        [
            ListItem(P("Train a net to replace measured synapse counts and still call it the FSOT product.", st["body"]), leftIndent=12),
            ListItem(P("Invent contacts, MDS brains, or unmeasured connectomes (bee / mosquito / plant / crow wiring).", st["body"]), leftIndent=12),
            ListItem(P("Mute aggression by fitness-hacking octopamine without a measured NT annotation.", st["body"]), leftIndent=12),
            ListItem(P("Call leftover olfactory LN mass or Kenyon/APL leftover a thought, or GABA a claimed inner state.", st["body"]), leftIndent=12),
            ListItem(P("Graft a human thalamus, 6-layer cortical column, or avian NCL onto FlyWire without a measured interface graph.", st["body"]), leftIndent=12),
            ListItem(P("Mix FSOT-2.1-Neural’s 0.005% mouse Allen claims with fly hop mass.", st["body"]), leftIndent=12),
        ],
        bulletType="bullet",
    ))
    closer.append(P("10. Next on the fly program (after this PDF)", st["h1"]))
    closer.append(tbl(
        [
            [P("<b>#</b>", b), P("<b>Work</b>", b), P("<b>Why</b>", b)],
            [P("1", c), P("Codex token: live DNg29 / JO type counts vs Male/BANC seeds", c),
             P("Still blocked — no CODEX_API_TOKEN. Hemibrain JO=78 / DNg29=0 already recorded.", c)],
            [P("2", c), P("Male/BANC same cell-type list (cross-sex identity)", c),
             P("Do not merge graphs into one fake animal", c)],
            [P("3", c), P("PHOT1 measured homolog if one appears", c),
             P("Still no_measured_map — not bulk MDS", c)],
        ],
        [0.4 * inch, 3.55 * inch, 3.15 * inch],
    ))
    closer.append(Spacer(1, 8))
    closer.append(P(
        "Boot: <font face='Courier'>python scripts/boot_pack.py --live --apis</font>. "
        "Math detail: MATH.md. Repos: REPOS.md. Map: MAP.md.",
        st["foot"],
    ))
    story.append(KeepTogether(closer))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.55 * inch,
        title="Bio-Neuromorphic Connectome Expansion Feasibility — FSOT fly program",
        author="FSOT fly pack (pin D1D38A)",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
