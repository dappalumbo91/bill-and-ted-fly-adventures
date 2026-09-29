theory FlySpine
  imports Main
begin

(* Fly obligation spine. Generated. Pin AEB2AD. *)

definition free_parameters :: nat where "free_parameters = 0"
definition phi_milli :: nat where "phi_milli = 1618"
definition inv_phi_milli :: nat where "inv_phi_milli = 618"
definition schlegel_n :: nat where "schlegel_n = 139248"
definition schlegel_dng29 :: nat where "schlegel_dng29 = 2"
definition schlegel_jo :: nat where "schlegel_jo = 1104"
definition meta_n :: nat where "meta_n = 144837"
definition meta_dng29 :: nat where "meta_dng29 = 2"
definition meta_jo :: nat where "meta_jo = 1107"
definition jo_only_meta :: nat where "jo_only_meta = 3"
definition jo_only_tsv :: nat where "jo_only_tsv = 0"
definition male_dng29 :: nat where "male_dng29 = 2"
definition male_jo :: nat where "male_jo = 672"
definition male_traced :: nat where "male_traced = 165122"
definition banc_dng29 :: nat where "banc_dng29 = 2"
definition banc_jo :: nat where "banc_jo = 1198"
definition hemibrain_dng29 :: nat where "hemibrain_dng29 = 0"
definition hemibrain_jo :: nat where "hemibrain_jo = 78"
definition hemibrain_typed :: nat where "hemibrain_typed = 22704"
definition male_neurons :: nat where "male_neurons = 165122"
definition male_gaba :: nat where "male_gaba = 22055"
definition male_edges :: nat where "male_edges = 25563197"
definition banc_neurons :: nat where "banc_neurons = 175401"
definition inventory_n :: nat where "inventory_n = 139248"
definition easy_n :: nat where "easy_n = 570"
definition easy_correct :: nat where "easy_correct = 570"
definition easy_wrong :: nat where "easy_wrong = 0"
definition easy_leftover :: nat where "easy_leftover = 0"
definition easy_consensus :: nat where "easy_consensus = 0"
definition challenge_n :: nat where "challenge_n = 299"
definition challenge_correct :: nat where "challenge_correct = 299"
definition challenge_wrong :: nat where "challenge_wrong = 0"
definition challenge_leftover :: nat where "challenge_leftover = 0"
definition challenge_consensus :: nat where "challenge_consensus = 0"
definition use_n :: nat where "use_n = 343"
definition use_correct :: nat where "use_correct = 343"
definition use_wrong :: nat where "use_wrong = 0"
definition leftover_n :: nat where "leftover_n = 35"
definition leftover_mapped :: nat where "leftover_mapped = 35"
definition guard_jo :: nat where "guard_jo = 1"
definition guard_vnc :: nat where "guard_vnc = 1"
definition guard_gaba :: nat where "guard_gaba = 1"
definition guard_courtship :: nat where "guard_courtship = 0"
definition guard_aggression :: nat where "guard_aggression = 0"
definition guard_fru_dsx :: nat where "guard_fru_dsx = 0"
definition trials :: nat where "trials = 3"
definition resource_reached :: nat where "resource_reached = 2"
definition measured_w_changed :: nat where "measured_w_changed = 0"
definition dng29_male_desc_milli :: nat where "dng29_male_desc_milli = 9204"
definition dng29_male_vm_milli :: nat where "dng29_male_vm_milli = 2088"
definition dng29_banc_desc_milli :: nat where "dng29_banc_desc_milli = 7813"
definition dng29_banc_vm_milli :: nat where "dng29_banc_vm_milli = 5827"
definition kcgm_male_desc_milli :: nat where "kcgm_male_desc_milli = 53"
definition kcgm_male_vm_milli :: nat where "kcgm_male_vm_milli = 0"
definition kcgm_banc_desc_milli :: nat where "kcgm_banc_desc_milli = 214"
definition kcgm_banc_vm_milli :: nat where "kcgm_banc_vm_milli = 0"
definition l5_male_desc_milli :: nat where "l5_male_desc_milli = 1916"
definition l5_male_vm_milli :: nat where "l5_male_vm_milli = 1"
definition l5_banc_desc_milli :: nat where "l5_banc_desc_milli = 3528"
definition l5_banc_vm_milli :: nat where "l5_banc_vm_milli = 0"
definition early_vm_milli :: nat where "early_vm_milli = 24254"
definition h07b_vm_milli :: nat where "h07b_vm_milli = 27566"
definition mbp3_vm_milli :: nat where "mbp3_vm_milli = 0"
definition early_n :: nat where "early_n = 7890"
definition h07b_n :: nat where "h07b_n = 954"
definition mbp3_n :: nat where "mbp3_n = 1038"

lemma ok_free: "free_parameters = 0"
  unfolding free_parameters_def by simp

lemma ok_jo_gap: "meta_jo = schlegel_jo + jo_only_meta"
  unfolding meta_jo_def schlegel_jo_def jo_only_meta_def by simp

lemma ok_inventory: "inventory_n = schlegel_n"
  unfolding inventory_n_def schlegel_n_def by simp

lemma ok_dng29: "male_dng29 = schlegel_dng29 \<and> banc_dng29 = schlegel_dng29 \<and> meta_dng29 = schlegel_dng29"
  unfolding male_dng29_def banc_dng29_def meta_dng29_def schlegel_dng29_def by eval

lemma ok_hemibrain: "hemibrain_dng29 = 0"
  unfolding hemibrain_dng29_def by simp

lemma ok_easy: "easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n"
  unfolding easy_correct_def easy_wrong_def easy_leftover_def easy_consensus_def easy_n_def by simp

lemma ok_challenge: "challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n"
  unfolding challenge_correct_def challenge_wrong_def challenge_leftover_def challenge_consensus_def challenge_n_def by simp

lemma ok_use: "use_correct + use_wrong = use_n"
  unfolding use_correct_def use_wrong_def use_n_def by simp

lemma ok_leftover: "leftover_mapped = leftover_n"
  unfolding leftover_mapped_def leftover_n_def by simp

lemma ok_dng_male: "dng29_male_desc_milli > 1000"
  unfolding dng29_male_desc_milli_def by eval

lemma ok_dng_banc: "dng29_banc_desc_milli > 1000"
  unfolding dng29_banc_desc_milli_def by eval

lemma ok_kcg_male: "kcgm_male_vm_milli \<le> 1000"
  unfolding kcgm_male_vm_milli_def by eval

lemma ok_kcg_banc: "kcgm_banc_vm_milli \<le> 1000"
  unfolding kcgm_banc_vm_milli_def by eval

lemma ok_l5_male: "l5_male_vm_milli \<le> 1000"
  unfolding l5_male_vm_milli_def by eval

lemma ok_l5_banc: "l5_banc_vm_milli \<le> 1000"
  unfolding l5_banc_vm_milli_def by eval

lemma ok_early: "early_vm_milli > 1000"
  unfolding early_vm_milli_def by eval

lemma ok_h07b: "h07b_vm_milli > 1000"
  unfolding h07b_vm_milli_def by eval

lemma ok_mbp3: "mbp3_vm_milli \<le> 1000"
  unfolding mbp3_vm_milli_def by eval

lemma ok_guard_jo: "guard_jo = 1"
  unfolding guard_jo_def by simp

lemma ok_guard_vnc: "guard_vnc = 1"
  unfolding guard_vnc_def by simp

lemma ok_guard_gaba: "guard_gaba = 1"
  unfolding guard_gaba_def by simp

lemma ok_guard_court: "guard_courtship = 0"
  unfolding guard_courtship_def by simp

lemma ok_guard_aggression: "guard_aggression = 0"
  unfolding guard_aggression_def by simp

lemma ok_guard_fru: "guard_fru_dsx = 0"
  unfolding guard_fru_dsx_def by simp

lemma ok_resource: "resource_reached \<le> trials"
  unfolding resource_reached_def trials_def by eval

end
