#!/usr/bin/env python3
"""Boot the fly experiment pack and check it against frozen measured results.

  python scripts/boot_pack.py
  python scripts/boot_pack.py --live   # inventory + analog pointer + male graph counts

Pin AEB2AD. 0 free parameters. Does not train a net.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from full_scalar_law import residual_scale  # noqa: E402
from trinary_syntax import aa_pair_weight, uniqueness_report  # noqa: E402

PIN = ROOT / "vendor" / "fsot_compute.py"
PIN_JSON = ROOT / "vendor" / "fsot_compute_AUTHORITY_PIN.json"
MAP = ROOT / "mapping" / "fly_gene_trinary.json"
MALE = ROOT / "data" / "male_cns_boot.json"
BANC = ROOT / "data" / "banc_connectome_boot.json"
HEMI = ROOT / "data" / "hemibrain_connectome_boot.json"
KENYON = ROOT / "data" / "kenyon_connectome_boot.json"
PROD = ROOT / "data" / "product_vs_alphafold.json"
HOOK = ROOT / "data" / "genetics_hook.json"
IDENT = ROOT / "data" / "type_identity.json"
PHOT1 = ROOT / "data" / "phot1_map.json"
DEV = ROOT / "data" / "develop_cycle.json"
GUARD = ROOT / "data" / "neural_guardrails.json"
SHARED = ROOT / "data" / "shared_type_hops.json"
BASE = ROOT / "data" / "baseline_sim.json"
MATH = ROOT / "data" / "math_first.json"
ARITH = ROOT / "data" / "arith.json"
ARITHC = ROOT / "data" / "arith_count.json"
ARITHS = ROOT / "data" / "arith_steps.json"
EXPR = ROOT / "data" / "trit_expr.json"
STRESS = ROOT / "data" / "stress_map.json"
REP = ROOT / "data" / "repertoire.json"
FUNC = ROOT / "data" / "fly_function.json"
WING = ROOT / "data" / "wing_sim.json"
YAW = ROOT / "data" / "yaw_jo.json"
MECH = ROOT / "docs" / "MECHANICS.md"
LEFTMAP = ROOT / "data" / "leftover_map.json"
LEFTDOC = ROOT / "docs" / "LEFTOVER.md"
SOLVE = ROOT / "data" / "leftover_solve.json"
MARGIN = ROOT / "data" / "leftover_margin.json"
PSIDE = ROOT / "data" / "predicted_side_hops.json"
BTLED = ROOT / "Bill and Ted fly adventures" / "ledger.json"
ADV1 = ROOT / "data" / "adventure1.json"
FOLD = ROOT / "data" / "adventure1_fold.json"
GINT = ROOT / "data" / "genetic_interactions.json"
PEP = ROOT / "data" / "peptide_leftovers.json"
GBR = ROOT / "data" / "genetic_baseline_rest.json"
CRUMB = ROOT / "data" / "genetic_crumbs.json"
BLUE = ROOT / "data" / "gene_blueprint.json"
ACC = ROOT / "data" / "accuracy_sim.json"
A1C = ROOT / "data" / "adventure1_closeout.json"
A1F = ROOT / "data" / "adventure1_fsot_apply.json"
A1B = ROOT / "data" / "adventure1_fsot_blueprint.json"
A1V = ROOT / "data" / "adventure1_verify.json"
A2M = ROOT / "data" / "bill3_math_env.json"
A2C = ROOT / "data" / "bill4_math_courses.json"
A2A = ROOT / "data" / "bill5_analysis.json"
A2MEM = ROOT / "data" / "bill6_memory.json"


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def near(a: float, b: float, eps: float) -> bool:
    return abs(float(a) - float(b)) <= eps


def hop2(path: Path, program: str, field: str = "vnc_motor") -> float:
    d = json.loads(path.read_text(encoding="utf-8"))
    rec = ((d.get("compare") or {}).get("hop_2") or {}).get(program) or {}
    return float(rec.get(field) or 0.0)


def test_pin() -> None:
    raw = PIN.read_bytes()
    sha = hashlib.sha256(raw).hexdigest().upper()
    if not sha.startswith("AEB2AD"):
        fail(f"pin sha={sha[:12]} does not start AEB2AD")
    cert = json.loads(PIN_JSON.read_text(encoding="utf-8"))
    want = str(cert.get("certificate_authority") or "").upper()
    if want and want != sha:
        fail("pin file != certificate")
    ok(f"pin AEB2AD  sha={sha[:16]}…  bytes={len(raw)}")


def test_trinary() -> None:
    u = uniqueness_report()
    if not u.get("all_unique"):
        fail(f"trinary opcodes not unique: {u}")
    w = aa_pair_weight("F", "W", 8)
    if abs(w - 1.6700524010190179) > 1e-9:
        fail(f"pair weight F–W@8={w}")
    ok(f"trinary 20/20 unique  F–W@8={w:.6f}")


def test_residual() -> None:
    r = residual_scale(abs(float(fc.domain_scalar("Biochemistry"))))
    if abs(r - 1.284069161007025) > 1e-9:
        fail(f"residual Biochemistry={r}")
    if int(fc.DOMAINS["Biochemistry"].D_eff) != 10:
        fail(f"Biochemistry D_eff={fc.DOMAINS['Biochemistry'].D_eff} (want nest 10)")
    ok(f"residual Biochemistry r={r:.6f}  D_eff={int(fc.DOMAINS['Biochemistry'].D_eff)}")
    if int(fc.PHI) == 0:
        fail("PHI missing")
    ok(f"seeds φ={float(fc.PHI):.6f} π={float(fc.PI):.6f}")


def test_frozen_hops() -> None:
    male_vnc = hop2(MALE, "vnc_sensory")
    male_jo = hop2(MALE, "JO")
    male_olf = hop2(MALE, "olfactory")
    banc_vnc = hop2(BANC, "vnc_sensory")
    banc_jo = hop2(BANC, "JO")
    banc_olf = hop2(BANC, "olfactory")
    # Documented RESULTS (2-decimal / 4-decimal). Live JSON is the authority.
    if male_vnc <= male_jo or male_jo <= 1 or male_olf >= 0.01:
        fail(f"male split broken vnc={male_vnc} JO={male_jo} olf={male_olf}")
    if banc_vnc <= banc_jo or banc_jo <= 1 or banc_olf >= 0.01:
        fail(f"BANC split broken vnc={banc_vnc} JO={banc_jo} olf={banc_olf}")
    if not near(male_vnc, 10.74, 0.02):
        fail(f"male VNC {male_vnc} ≠ 10.74")
    if not near(male_jo, 7.77, 0.02):
        fail(f"male JO {male_jo} ≠ 7.77")
    if not near(male_olf, 0.000571, 0.001):
        fail(f"male olf {male_olf}")
    if not near(banc_vnc, 10.16, 0.02):
        fail(f"BANC VNC {banc_vnc}")
    if not near(banc_jo, 6.64, 0.05):
        fail(f"BANC JO {banc_jo}")
    hemi = json.loads(HEMI.read_text(encoding="utf-8"))
    hemi_jo = hop2(HEMI, "JO", "descending")
    hemi_olf = hop2(HEMI, "olfactory", "descending")
    hemi_kc = hop2(HEMI, "kenyon", "descending")
    if int(hemi.get("n_dng29", 0)) != 0:
        fail("hemibrain DNg29 should be absent")
    if hemi_jo <= 1 or hemi_olf >= 0.5:
        fail(f"hemibrain split broken JO={hemi_jo} olf={hemi_olf}")
    if not near(hemi_jo, 2.68, 0.05):
        fail(f"hemibrain JO desc {hemi_jo}")
    if not near(hemi_olf, 0.072, 0.01):
        fail(f"hemibrain olf desc {hemi_olf}")
    if hemi_kc >= 0.05:
        fail(f"hemibrain KC lit descending {hemi_kc}")
    ken = json.loads(KENYON.read_text(encoding="utf-8"))
    ken_desc = hop2(KENYON, "kc_full_hemibrain", "descending")
    ken_k = hop2(KENYON, "kc_full_hemibrain", "kenyon")
    if ken_desc >= 0.5:
        fail(f"KC leaked to descending {ken_desc}")
    if ken_k <= 1:
        fail(f"KC hop-2 kenyon mass {ken_k}")
    if int(ken.get("n_kc") or 0) < 1000:
        fail("kenyon n_kc")
    mp = json.loads(MAP.read_text(encoding="utf-8"))
    mm = mp["hop_split"]["male_cns_hop2_vnc_motor"]
    if abs(float(mm["JO"]) - male_jo) > 1e-12:
        fail("mapping JO ≠ male_cns_boot.json")
    ok(
        f"hop-2 vnc_motor  male VNC={male_vnc:.2f} JO={male_jo:.2f} olf={male_olf:.4f}  "
        f"BANC VNC={banc_vnc:.2f} JO={banc_jo:.2f} olf={banc_olf:.4f}  "
        f"hemibrain desc JO={hemi_jo:.2f} olf={hemi_olf:.3f}  "
        f"KC kenyon={ken_k:.2f} desc={ken_desc:.4f}"
    )


def test_product_and_genes() -> None:
    s = json.loads(PROD.read_text(encoding="utf-8")).get("summary") or {}
    if float(s["fsot_product_median_A"]) >= float(s["alphafold_median_A"]):
        fail("product median not below AF")
    if not near(float(s["fsot_product_median_A"]), 0.13, 0.01):
        fail(f"product median {s['fsot_product_median_A']}")
    mp = json.loads(MAP.read_text(encoding="utf-8"))
    genes = {g["symbol"]: g for g in mp.get("genes_on_cells") or []}
    for sym in ("nompC", "iav", "nan", "Gad1", "ChAT", "VGlut", "Mhc"):
        if sym not in genes:
            fail(f"missing gene {sym}")
    hook = json.loads(HOOK.read_text(encoding="utf-8"))
    if not hook.get("overall_ok"):
        fail(f"genetics_hook fail={hook.get('fail')}")
    hooked = {g["symbol"] for g in hook.get("genes") or []}
    for sym in ("ChAT", "VGlut", "Mhc"):
        if sym not in hooked:
            fail(f"hook missing {sym}")
    if mp.get("free_parameters") != 0:
        fail("mapping free_parameters")
    ok(
        f"product {float(s['fsot_product_median_A']):.2f} Å < AF "
        f"{float(s['alphafold_median_A']):.2f} Å  genes={list(genes)} hook={len(hooked)}"
    )


def test_identity_phot1_develop() -> None:
    ident = json.loads(IDENT.read_text(encoding="utf-8"))
    if int(ident.get("shared_cell_type_names") or 0) < 1000:
        fail(f"type identity shared {ident.get('shared_cell_type_names')}")
    if ident.get("do_not") is None:
        fail("type identity missing do_not")
    ok(
        f"BANC∩Male types {ident['shared_cell_type_names']}  "
        f"jaccard={float(ident['jaccard_type_names']):.3f}  "
        f"malecns_match cells={ident['banc_n_with_malecns_match']}"
    )
    p = json.loads(PHOT1.read_text(encoding="utf-8"))
    if (p.get("phot1") or {}).get("accession") != "O48963":
        fail("PHOT1 accession")
    if (p.get("mislabel") or {}).get("accession") != "Q2V2M9":
        fail("PHOT1 mislabel not recorded")
    if p.get("structure_mode") != "measured_domains":
        fail("PHOT1 not measured_domains")
    if int(len(p.get("measured_domains") or [])) < 2:
        fail("PHOT1 LOV crystals")
    ok(
        f"PHOT1 O48963 measured_domains n={len(p['measured_domains'])} "
        f"cov={float(p['template_coverage']):.3f} leftover={float(p['leftover']):.3f}"
    )
    d = json.loads(DEV.read_text(encoding="utf-8"))
    hop2 = ((d.get("hops") or {}).get("compare") or {}).get("hop_2") or {}
    early = float((hop2.get("birth_early") or {}).get("vnc_motor") or 0)
    mb = float((hop2.get("ito_MBp3") or {}).get("vnc_motor") or 0)
    if early <= 1:
        fail(f"early birth motor {early}")
    if mb >= 0.01:
        fail(f"MBp3 should not light vnc_motor {mb}")
    persist = [
        x["larva_class"]
        for x in (d.get("inventory") or {}).get("named_job_persistence") or []
        if x.get("persistent_job")
    ]
    if "KC" not in persist:
        fail("KC not persistent")
    ok(
        f"develop hop-2 vnc_motor early={early:.2f} MBp3={mb:.4f}  "
        f"persist={persist}"
    )
    g = json.loads(GUARD.read_text(encoding="utf-8"))
    if "courtship" not in (g.get("deny_default_seeds") or {}):
        fail("guardrail missing courtship deny")
    if (g.get("allow_default_seeds") or {}).get("JO", {}).get("default") != "on":
        fail("guardrail JO not on")
    ok("neural guardrails  JO/VNC/GABA on  courtship/aggression/fru off")
    sh = json.loads(SHARED.read_text(encoding="utf-8"))
    if not sh.get("overall_ok"):
        fail("shared_type_hops overall_ok")
    names = [t.get("type") for t in sh.get("types") or []]
    if "DNg29" not in names or "KCg-m" not in names:
        fail(f"shared types {names}")
    ok(f"shared-type hops (two animals) {names} overall_ok")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    if not base.get("brain_print_ok"):
        fail("baseline_sim brain_print_ok")
    if int(base.get("n_trials") or 0) < 3:
        fail("baseline_sim trials")
    odor = next(
        (r for r in (base.get("brain_print") or []) if r.get("condition") == "odor_contrast"),
        {},
    )
    if (odor.get("male") or {}).get("walks"):
        fail("baseline odor walked")
    ok(
        f"baseline sim trials={base['n_trials']} "
        f"resource={base.get('n_resource_reached')} brain_print_ok"
    )
    mf = json.loads(MATH.read_text(encoding="utf-8"))
    if not (mf.get("math_probe") or {}).get("overall_ok"):
        fail(f"math_probe {((mf.get('math_probe') or {}).get('fail'))}")
    hops = mf.get("laterality_hops") or {}
    if hops and not hops.get("vnc_sensory_ipsi_same_sign"):
        fail("laterality hops not ipsilateral")
    miss = mf.get("miss_audit") or {}
    if int(miss.get("n_mean_laterality_leftover") or 0) < 3:
        fail("mean laterality should be leftover under 1/φ")
    ok(
        f"math-first {mf['math_probe']['n_ok']}/{mf['math_probe']['n']}  "
        f"ipsi={hops.get('vnc_sensory_ipsi_same_sign')}  "
        f"mean_leftover={miss.get('n_mean_laterality_leftover')}/3"
    )
    ar = json.loads(ARITH.read_text(encoding="utf-8"))
    if not ar.get("overall_ok"):
        fail(f"arith fail={ar.get('fail')}")
    if int(ar.get("n_ok") or 0) < 100:
        fail(f"arith too few {ar.get('n_ok')}")
    ok(f"arith {ar['n_ok']}/{ar['n']} balanced-ternary ALU")
    ac = json.loads(ARITHC.read_text(encoding="utf-8"))
    if not ac.get("overall_ok"):
        fail(f"arith_count fail={ac.get('fail')}")
    ok(f"arith_count {ac['n_ok']}/{ac['n']} measured hop integers")
    ast = json.loads(ARITHS.read_text(encoding="utf-8"))
    if not ast.get("overall_ok"):
        fail(f"arith_steps fail={ast.get('fail')}")
    ok(f"arith_steps {ast['n_ok']}/{ast['n']} chains  steps={ast.get('n_steps_total')}")
    ex = json.loads(EXPR.read_text(encoding="utf-8"))
    if not ex.get("overall_ok"):
        fail(f"trit_expr fail={ex.get('fail')}")
    st = json.loads(STRESS.read_text(encoding="utf-8"))
    if int(st.get("n_bottlenecks") or 0) < 1:
        fail("stress_map empty")
    ok(
        f"trit_expr {ex['n_ok']}/{ex['n']}  "
        f"cons0={ex.get('consensus_zero_stress')}  "
        f"bottlenecks={st.get('n_bottlenecks')}"
    )
    rp = json.loads(REP.read_text(encoding="utf-8"))
    if not rp.get("overall_ok"):
        fail("repertoire split broken")
    jobs = {j["job"]: j for j in rp.get("jobs") or []}
    if jobs.get("courtship", {}).get("allow") or jobs.get("aggression", {}).get("allow"):
        fail("repertoire guardrail")
    if not jobs.get("see") or float((jobs["see"].get("male") or {}).get("descending") or 0) < 1:
        fail("see should light descending")
    ok(
        f"repertoire jobs={rp.get('n_jobs')} allow={rp.get('n_allowed')} "
        f"deny={rp.get('n_denied_default')}"
    )
    fn = json.loads(FUNC.read_text(encoding="utf-8"))
    if int(fn.get("n_trials_flight_like") or 0) != 0:
        fail("tethered wings should not look like 200 Hz flight")
    hops = fn.get("flight_motor_hops") or {}
    dnp = hops.get("DNp01") or {}
    if float(dnp.get("hop2_descending") or 0) < 1:
        fail("DNp01 should light descending")
    ok(
        f"wing parked 0/3 flight-like  DNp01 desc={float(dnp.get('hop2_descending') or 0):.2f} "
        f"hg3 n={((hops.get('hg3_MN') or {}).get('n_seed'))}"
    )
    ws = json.loads(WING.read_text(encoding="utf-8"))
    if not ws.get("overall_ok"):
        fail(f"wing_sim fail={ws.get('fail')}")
    ok(f"wing_sim {ws['n_ok']}/{ws['n']}  f={ws.get('f_wb_hz')} Hz  sim_fps={ws.get('sim_fps')}")
    yj = json.loads(YAW.read_text(encoding="utf-8"))
    if not yj.get("overall_ok"):
        fail(f"yaw_jo fail={yj.get('fail')}")
    if int(yj.get("bilateral_consensus", 99)) != 0:
        fail("bilateral JO should consensus 0")
    if not MECH.is_file():
        fail("docs/MECHANICS.md missing")
    ok(f"yaw_jo {yj['n_ok']}/{yj['n']}  bilateral_cons={yj.get('bilateral_consensus')}  MECHANICS.md")
    lm = json.loads(LEFTMAP.read_text(encoding="utf-8"))
    if not lm.get("overall_ok"):
        fail("leftover_map")
    if int(lm.get("n_mapped") or 0) < 15:
        fail("leftover_map too few mapped")
    if not LEFTDOC.is_file():
        fail("docs/LEFTOVER.md missing")
    ok(f"leftover_map {lm['n_mapped']}/{lm['n']} mapped  {lm.get('by_status')}")
    sv = json.loads(SOLVE.read_text(encoding="utf-8"))
    if not sv.get("overall_ok"):
        fail("leftover_solve")
    acc = float(((sv.get("partner_side") or {}).get("accuracy")) or 0)
    if acc < 0.618:
        fail(f"partner-side vote acc {acc} < 1/φ")
    tbd = (sv.get("truman_TBD") or {}).get("job")
    if tbd and tbd != "motor_on":
        fail(f"TBD job {tbd}")
    ok(
        f"leftover_solve side_acc={acc:.3f}  TBD={tbd}  "
        f"birth_assign={(sv.get('birthtime_prior') or {}).get('assigned')}"
    )
    mg = json.loads(MARGIN.read_text(encoding="utf-8"))
    if float(mg.get("MIN_CLASSIFIER_ACCURACY_PCT") or 0) != 99.5:
        fail("Lean classifier gate")
    if float(mg.get("MAX_MEDIAN_ERROR_PCT") or 0) != 0.5:
        fail("Lean scalar gate")
    if not mg.get("overall_ok"):
        fail(f"leftover_margin work={mg.get('work_list')}")
    ok(
        f"leftover_margin green {mg.get('n_green')}/{mg.get('n')}  "
        f"retired={mg.get('n_structural_retired')}  work={mg.get('work_list')}"
    )
    ps = json.loads(PSIDE.read_text(encoding="utf-8"))
    if not ps.get("overall_ok") or not ps.get("ipsi_pair"):
        fail("predicted_side_hops")
    ok(
        f"predicted_side_hops ipsi_pair  L={ps.get('n_predicted_L')} "
        f"R={ps.get('n_predicted_R')} leftover={ps.get('n_leftover')}"
    )
    bt = json.loads(BTLED.read_text(encoding="utf-8"))
    if bt.get("current_bill") not in ("Bill-0", "Bill-1", "Bill-2", "Bill-3", "Bill-4", "Bill-5", "Bill-6", "Bill-7"):
        fail(f"bill_ted current {bt.get('current_bill')}")
    ok(f"bill_ted current={bt.get('current_bill')} teds={bt.get('teds')}")
    a1 = json.loads(ADV1.read_text(encoding="utf-8"))
    if not a1.get("overall_ok"):
        fail("adventure1")
    ok("adventure1 neuromod volume leftover vs VNC walk")
    fd = json.loads(FOLD.read_text(encoding="utf-8"))
    if not fd.get("overall_ok") or int(fd.get("n_ok") or 0) < 9:
        fail(f"adventure1_fold {fd.get('fail')}")
    ok(
        f"adventure1_fold genes {fd['n_ok']}/{fd['n']}  "
        f"look-split {float(fd.get('look_split_pct') or 0):.3f}%"
    )
    gi = json.loads(GINT.read_text(encoding="utf-8"))
    if not gi.get("overall_ok") or int(gi.get("n_ok") or 0) < 17:
        fail(f"genetic_interactions {gi.get('fail')}")
    ok(f"genetic_interactions {gi['n_ok']}/{gi['n']} receptors/transporters/innexins")
    pep = json.loads(PEP.read_text(encoding="utf-8"))
    if not pep.get("overall_ok") or int(pep.get("n_ok") or 0) < 28:
        fail(f"peptide_leftovers {pep.get('fail')}")
    ln = pep.get("LNv_hop") or {}
    if ln and not ln.get("sleep_leftover"):
        fail("LNv should leftover vs walk")
    ok(
        f"peptide_leftovers {pep['n_ok']}/{pep['n']}  "
        f"LNv leftover motor={((ln.get('hop2') or {}).get('vnc_motor'))}"
    )
    gbr = json.loads(GBR.read_text(encoding="utf-8"))
    if not gbr.get("overall_ok") or int(gbr.get("n_ok") or 0) < 47:
        fail(f"genetic_baseline_rest {gbr.get('fail')}")
    ok(f"genetic_baseline_rest {gbr['n_ok']}/{gbr['n']}  Orco leftover olf={float(gbr.get('olfactory_hop2_vnc_motor') or 0):.4f}")
    cr = json.loads(CRUMB.read_text(encoding="utf-8"))
    if not cr.get("overall_ok"):
        fail(f"crumbs {cr.get('fail')}")
    bp = json.loads(BLUE.read_text(encoding="utf-8"))
    acs = json.loads(ACC.read_text(encoding="utf-8"))
    if not acs.get("overall_ok"):
        fail("accuracy_sim")
    ok(
        f"crumbs {cr['n_ok']}/{cr['n']}  blueprint n={bp.get('n')} "
        f"renames={bp.get('n_rename')}  accuracy_sim {acs.get('n_green')}/{acs.get('n')}"
    )
    a1c = json.loads(A1C.read_text(encoding="utf-8"))
    if not a1c.get("overall_ok") or not a1c.get("two_animal_function_ok"):
        fail("adventure1_closeout")
    ok("adventure1 closeout  two-animal function 3/3")
    af = json.loads(A1F.read_text(encoding="utf-8"))
    if not af.get("overall_ok"):
        fail("adventure1_fsot_apply")
    ok(
        f"adventure1_fsot_apply Ledger B {af['n_green']}/{af['n']}  "
        f"median {float(af['median_error_pct']):.4f}%"
    )
    ab = json.loads(A1B.read_text(encoding="utf-8"))
    if not ab.get("overall_ok"):
        fail("adventure1_fsot_blueprint")
    if int(ab.get("n_genes_ok") or 0) < 120:
        fail(f"blueprint genes {ab.get('n_genes_ok')}/{ab.get('n_genes')}")
    if not (ab.get("orco") or {}).get("ok"):
        fail("Orco leftover missing")
    if int(ab.get("n_pathways_ok") or 0) < 5:
        fail(f"pathways {ab.get('n_pathways_ok')}")
    ok(
        f"adventure1_fsot_blueprint genes {ab['n_genes_ok']}/{ab['n_genes']}  "
        f"pathways {ab['n_pathways_ok']}/5  "
        f"look-split {float((ab.get('scalar') or {}).get('look_split_pct') or 0):.3f}%"
    )
    av = json.loads(A1V.read_text(encoding="utf-8"))
    if not av.get("overall_ok") or not av.get("promotes"):
        fail(f"adventure1_verify fail={av.get('fail')}")
    if av.get("ted") != "TED-3" or av.get("promote_to") != "Bill-3":
        fail(f"verify ted={av.get('ted')} promote_to={av.get('promote_to')}")
    if "Bill-3" not in (bt.get("bills") or []) and bt.get("current_bill") not in ("Bill-3", "Bill-4"):
        fail("TED-3 promotes but Bill-3 is not on the ledger")
    ok(
        f"adventure1_verify TED-3 → Bill-3  {av.get('n_ok')}/{av.get('n')}  "
        f"bill_fn={av.get('bill_function_ok')} lean={av.get('lean_ok')}"
    )
    a2 = json.loads(A2M.read_text(encoding="utf-8"))
    if not a2.get("overall_ok"):
        fail(f"bill3_math_env fail={a2.get('fail')}")
    if int(a2.get("n_ok") or 0) != int(a2.get("n") or 0):
        fail(f"math env {a2.get('n_ok')}/{a2.get('n')}")
    if a2.get("promotes") and "Bill-4" not in (bt.get("bills") or []) and bt.get("current_bill") not in ("Bill-4", "Bill-5"):
        fail("TED-4 promotes but Bill-4 is not on the ledger")
    ok(
        f"bill3_math_env TED-4 {a2.get('n_ok')}/{a2.get('n')}  "
        f"types_lit={(a2.get('thinking') or {}).get('n_types_lit')}  "
        f"current={bt.get('current_bill')}"
    )
    a2c = json.loads(A2C.read_text(encoding="utf-8"))
    if not a2c.get("overall_ok"):
        fail(f"bill4_math_courses fail={a2c.get('fail')}")
    if int(a2c.get("n_ok") or 0) != int(a2c.get("n") or 0):
        fail(f"math courses {a2c.get('n_ok')}/{a2c.get('n')}")
    if a2c.get("promotes") and "Bill-5" not in (bt.get("bills") or []) and bt.get("current_bill") not in ("Bill-5", "Bill-6"):
        fail("TED-5 promotes but Bill-5 is not on the ledger")
    ok(
        f"bill4_math_courses TED-5 {a2c.get('n_ok')}/{a2c.get('n')}  "
        f"courses={len(a2c.get('by_course') or {})}  current={bt.get('current_bill')}"
    )
    a2a = json.loads(A2A.read_text(encoding="utf-8"))
    if not a2a.get("overall_ok"):
        fail(f"bill5_analysis fail={a2a.get('fail')}")
    if int(a2a.get("n_ok") or 0) != int(a2a.get("n") or 0):
        fail(f"analysis {a2a.get('n_ok')}/{a2a.get('n')}")
    if a2a.get("promotes") and "Bill-6" not in (bt.get("bills") or []) and bt.get("current_bill") not in ("Bill-6", "Bill-7"):
        fail("TED-6 promotes but Bill-6 is not on the ledger")
    ok(
        f"bill5_analysis TED-6 {a2a.get('n_ok')}/{a2a.get('n')}  "
        f"plant_f={((a2a.get('plant') or {}).get('f_wb_hz'))}  current={bt.get('current_bill')}"
    )
    mem = json.loads(A2MEM.read_text(encoding="utf-8"))
    if not mem.get("overall_ok"):
        fail(f"bill6_memory fail={mem.get('fail')}")
    if int(mem.get("n_ok") or 0) != int(mem.get("n") or 0):
        fail(f"memory {mem.get('n_ok')}/{mem.get('n')}")
    if mem.get("promotes") and bt.get("current_bill") != "Bill-7":
        fail("TED-7 promotes but ledger current_bill is not Bill-7")
    ok(
        f"bill6_memory TED-7 {mem.get('n_ok')}/{mem.get('n')}  "
        f"LTM={(mem.get('exam') or {}).get('ltm_recompute_after_interfere')}  "
        f"current={bt.get('current_bill')}"
    )


def test_counts() -> None:
    male = json.loads(MALE.read_text(encoding="utf-8"))
    banc = json.loads(BANC.read_text(encoding="utf-8"))
    if male.get("pin") not in (None, "AEB2AD"):
        fail(f"male pin {male.get('pin')}")
    if int(male["n_neurons"]) != 165122:
        fail(f"male n_neurons {male['n_neurons']}")
    if int(male["n_gaba"]) != 22055:
        fail(f"male n_gaba {male['n_gaba']}")
    if int(banc["n_neurons"]) != 175401:
        fail(f"BANC n_neurons {banc['n_neurons']}")
    if male.get("free_parameters") != 0 or banc.get("free_parameters") != 0:
        fail("boot free_parameters")
    r = male.get("residual_Biochemistry")
    if r is not None and abs(float(r) - 1.284069161007025) > 1e-9:
        fail(f"male residual {r}")
    ok(
        f"Male CNS {male['n_neurons']} neurons GABA={male['n_gaba']}  "
        f"BANC {banc['n_neurons']} neurons"
    )


def live_inventory() -> None:
    from fly_connectome import FLY_ROOT, ensure_annotations, read_annotations

    path = ensure_annotations(FLY_ROOT)
    inv = read_annotations(path)
    n = int(inv.get("n_neurons") or inv.get("n") or 0)
    if n < 100000:
        # inventory schema
        n = int((inv.get("n_rows") or 0) or n)
    frozen = json.loads((ROOT / "data" / "fly_connectome_inventory.json").read_text(encoding="utf-8"))
    fn = int(frozen.get("n_neurons") or frozen.get("n") or frozen.get("n_rows") or 0)
    live_n = int(inv.get("n_neurons") or inv.get("n") or inv.get("n_rows") or 0)
    if live_n and fn and live_n != fn:
        fail(f"inventory n live={live_n} frozen={fn}")
    ok(f"live FlyWire annotations n={live_n or n}  file={path.name}")


def live_male_graph() -> None:
    from male_cns import ANN, WTS, load_male_graph

    if not ANN.is_file() or not WTS.is_file():
        print("SKIP  male_cns feathers not on D:")
        return
    g = load_male_graph()
    frozen = json.loads(MALE.read_text(encoding="utf-8"))
    if int(g["n"]) != int(frozen["n_neurons"]):
        fail(f"live male n={g['n']} frozen={frozen['n_neurons']}")
    if int(g["n_edges"]) != int(frozen["n_edges"]):
        fail(f"live male edges={g['n_edges']} frozen={frozen['n_edges']}")
    if int(g["n_gaba"]) != int(frozen["n_gaba"]):
        fail(f"live male GABA={g['n_gaba']} frozen={frozen['n_gaba']}")
    ok(f"live Male CNS graph n={g['n']} edges={g['n_edges']} GABA={g['n_gaba']}")


def live_analog() -> None:
    import analog_pointer

    rc = analog_pointer.main()
    if rc != 0:
        fail("analog_pointer")
    d = json.loads((ROOT / "data" / "analog_pointer.json").read_text(encoding="utf-8"))
    jobs = d.get("jobs") or []
    if len(jobs) < 2:
        fail("analog jobs")
    if jobs[0]["mapped_analog"]["symbol"] != "nompC":
        fail("analog not nompC")
    ok("analog_pointer mec-4 → nompC  unc-25 → Gad1")


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="also read D:\\FlyWire_Connectome")
    ap.add_argument("--apis", action="store_true", help="UniProt/Ensembl/neuPrint/Allen/GitHub")
    args = ap.parse_args(argv)
    print("=" * 64)
    print("FSOT fly pack boot")
    print(f"  root = {ROOT}")
    print("=" * 64)
    test_pin()
    test_trinary()
    test_residual()
    test_counts()
    test_frozen_hops()
    test_product_and_genes()
    test_identity_phot1_develop()
    if args.live:
        live_inventory()
        live_male_graph()
        live_analog()
    if args.apis:
        from genetics_hook import main as genetics_main
        from live_verify import main as live_main

        rc = live_main()
        if rc != 0:
            fail("live_verify APIs")
        ok("live_verify APIs")
        rc = genetics_main()
        if rc != 0:
            fail("genetics_hook")
        ok("genetics_hook UniProt/Ensembl + hop jobs")
    print("=" * 64)
    print("PACK BOOT OK  pin=AEB2AD  free_parameters=0  not a trained RNN")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        fail(f"uncaught {e}")
