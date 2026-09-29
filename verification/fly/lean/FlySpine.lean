-- Fly obligation spine. Pin AEB2AD. 0 free parameters.
-- Generated from committed JSON by verification/export_fly_spine.py.
-- A missing measurement stays none. The gate is the test, not a filled count.

def pin : String := "AEB2AD"
def freeParameters : Nat := 0

def commit {α : Type} [DecidableEq α] (votes : List α) : Option α :=
  match votes.eraseDups with
  | [a] => some a
  | _ => none

#guard freeParameters = 0
#guard pin = "AEB2AD"
#guard commit ["reflect"] = some "reflect"
#guard commit ([] : List String) = none
#guard commit ["rain", "drought"] = none
#guard commit ["gas", "gas"] = some "gas"

def free_parameters : Nat := 0
def phi_milli : Nat := 1618
def inv_phi_milli : Nat := 618
def schlegel_n : Nat := 139248
def schlegel_dng29 : Nat := 2
def schlegel_jo : Nat := 1104
def meta_n : Nat := 144837
def meta_dng29 : Nat := 2
def meta_jo : Nat := 1107
def jo_only_meta : Nat := 3
def jo_only_tsv : Nat := 0
def male_dng29 : Nat := 2
def male_jo : Nat := 672
def male_traced : Nat := 165122
def banc_dng29 : Nat := 2
def banc_jo : Nat := 1198
def hemibrain_dng29 : Nat := 0
def hemibrain_jo : Nat := 78
def hemibrain_typed : Nat := 22704
def male_neurons : Nat := 165122
def male_gaba : Nat := 22055
def male_edges : Nat := 25563197
def banc_neurons : Nat := 175401
def inventory_n : Nat := 139248
def easy_n : Nat := 570
def easy_correct : Nat := 570
def easy_wrong : Nat := 0
def easy_leftover : Nat := 0
def easy_consensus : Nat := 0
def challenge_n : Nat := 299
def challenge_correct : Nat := 299
def challenge_wrong : Nat := 0
def challenge_leftover : Nat := 0
def challenge_consensus : Nat := 0
def use_n : Nat := 343
def use_correct : Nat := 343
def use_wrong : Nat := 0
def leftover_n : Nat := 35
def leftover_mapped : Nat := 35
def guard_jo : Nat := 1
def guard_vnc : Nat := 1
def guard_gaba : Nat := 1
def guard_courtship : Nat := 0
def guard_aggression : Nat := 0
def guard_fru_dsx : Nat := 0
def trials : Nat := 3
def resource_reached : Nat := 2
def measured_w_changed : Nat := 0
def dng29_male_desc_milli : Nat := 9204
def dng29_male_vm_milli : Nat := 2088
def dng29_banc_desc_milli : Nat := 7813
def dng29_banc_vm_milli : Nat := 5827
def kcgm_male_desc_milli : Nat := 53
def kcgm_male_vm_milli : Nat := 0
def kcgm_banc_desc_milli : Nat := 214
def kcgm_banc_vm_milli : Nat := 0
def l5_male_desc_milli : Nat := 1916
def l5_male_vm_milli : Nat := 1
def l5_banc_desc_milli : Nat := 3528
def l5_banc_vm_milli : Nat := 0
def early_vm_milli : Nat := 24254
def h07b_vm_milli : Nat := 27566
def mbp3_vm_milli : Nat := 0
def early_n : Nat := 7890
def h07b_n : Nat := 954
def mbp3_n : Nat := 1038

theorem jo_gap : meta_jo = schlegel_jo + jo_only_meta := by decide
theorem jo_only_tsv_zero : jo_only_tsv = 0 := by decide
theorem inventory_is_schlegel : inventory_n = schlegel_n := by decide
theorem dng29_four : male_dng29 = schlegel_dng29 ∧ banc_dng29 = schlegel_dng29 ∧ meta_dng29 = schlegel_dng29 := by decide
theorem hemibrain_no_dng29 : hemibrain_dng29 = 0 := by decide
theorem easy_partition : easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n := by decide
theorem challenge_partition : challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n := by decide
theorem use_partition : use_correct + use_wrong = use_n := by decide
theorem use_no_wrong : use_wrong = 0 := by decide
theorem leftover_closed : leftover_mapped = leftover_n := by decide
theorem dng29_male_desc_on : dng29_male_desc_milli > 1000 := by decide
theorem dng29_banc_desc_on : dng29_banc_desc_milli > 1000 := by decide
theorem kcgm_male_motor_off : kcgm_male_vm_milli ≤ 1000 := by decide
theorem kcgm_banc_motor_off : kcgm_banc_vm_milli ≤ 1000 := by decide
theorem l5_male_motor_off : l5_male_vm_milli ≤ 1000 := by decide
theorem l5_banc_motor_off : l5_banc_vm_milli ≤ 1000 := by decide
theorem early_motor_on : early_vm_milli > 1000 := by decide
theorem h07b_motor_on : h07b_vm_milli > 1000 := by decide
theorem mbp3_motor_off : mbp3_vm_milli ≤ 1000 := by decide
theorem guards_on : guard_jo = 1 ∧ guard_vnc = 1 ∧ guard_gaba = 1 := by decide
theorem guards_off : guard_courtship = 0 ∧ guard_aggression = 0 ∧ guard_fru_dsx = 0 := by decide
theorem resource_within_trials : resource_reached ≤ trials := by decide

def codexDNg29Gate (exportCount : Nat) : Bool := exportCount = schlegel_dng29
def joExportGate (exportJO : Nat) : Bool := exportJO = schlegel_jo || exportJO = meta_jo
def fcaBodyIdCount : Option Nat := none
def pupalFrameCount : Option Nat := none
def iwasakiFrameCount : Option Nat := none

theorem codex_gate_accepts_schlegel : codexDNg29Gate schlegel_dng29 = true := by decide
theorem codex_gate_rejects_zero : codexDNg29Gate 0 = false := by decide
theorem jo_gate_accepts_split : joExportGate schlegel_jo = true := by decide
theorem jo_gate_accepts_coarse : joExportGate meta_jo = true := by decide
theorem jo_gate_rejects_zero : joExportGate 0 = false := by decide
theorem fca_bodyid_unseen : fcaBodyIdCount = none := by rfl
theorem pupal_frames_unseen : pupalFrameCount = none := by rfl
theorem iwasaki_frames_unseen : iwasakiFrameCount = none := by rfl
