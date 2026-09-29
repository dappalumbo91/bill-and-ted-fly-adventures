(* Fly obligation spine. Generated. Pin AEB2AD. Prelude only. *)

Definition free_parameters := 0.
Definition phi_milli := 1618.
Definition inv_phi_milli := 618.
Definition schlegel_n := 139248.
Definition schlegel_dng29 := 2.
Definition schlegel_jo := 1104.
Definition meta_n := 144837.
Definition meta_dng29 := 2.
Definition meta_jo := 1107.
Definition jo_only_meta := 3.
Definition jo_only_tsv := 0.
Definition male_dng29 := 2.
Definition male_jo := 672.
Definition male_traced := 165122.
Definition banc_dng29 := 2.
Definition banc_jo := 1198.
Definition hemibrain_dng29 := 0.
Definition hemibrain_jo := 78.
Definition hemibrain_typed := 22704.
Definition male_neurons := 165122.
Definition male_gaba := 22055.
Definition male_edges := 25563197.
Definition banc_neurons := 175401.
Definition inventory_n := 139248.
Definition easy_n := 570.
Definition easy_correct := 570.
Definition easy_wrong := 0.
Definition easy_leftover := 0.
Definition easy_consensus := 0.
Definition challenge_n := 299.
Definition challenge_correct := 299.
Definition challenge_wrong := 0.
Definition challenge_leftover := 0.
Definition challenge_consensus := 0.
Definition use_n := 343.
Definition use_correct := 343.
Definition use_wrong := 0.
Definition leftover_n := 35.
Definition leftover_mapped := 35.
Definition guard_jo := 1.
Definition guard_vnc := 1.
Definition guard_gaba := 1.
Definition guard_courtship := 0.
Definition guard_aggression := 0.
Definition guard_fru_dsx := 0.
Definition trials := 3.
Definition resource_reached := 2.
Definition measured_w_changed := 0.
Definition dng29_male_desc_milli := 9204.
Definition dng29_male_vm_milli := 2088.
Definition dng29_banc_desc_milli := 7813.
Definition dng29_banc_vm_milli := 5827.
Definition kcgm_male_desc_milli := 53.
Definition kcgm_male_vm_milli := 0.
Definition kcgm_banc_desc_milli := 214.
Definition kcgm_banc_vm_milli := 0.
Definition l5_male_desc_milli := 1916.
Definition l5_male_vm_milli := 1.
Definition l5_banc_desc_milli := 3528.
Definition l5_banc_vm_milli := 0.
Definition early_vm_milli := 24254.
Definition h07b_vm_milli := 27566.
Definition mbp3_vm_milli := 0.
Definition early_n := 7890.
Definition h07b_n := 954.
Definition mbp3_n := 1038.

Lemma ok_free_parameters : free_parameters = 0.
Proof. reflexivity. Qed.
Lemma ok_jo_gap : meta_jo = schlegel_jo + jo_only_meta.
Proof. reflexivity. Qed.
Lemma ok_jo_only_tsv : jo_only_tsv = 0.
Proof. reflexivity. Qed.
Lemma ok_inventory : inventory_n = schlegel_n.
Proof. reflexivity. Qed.
Lemma ok_dng29_male : male_dng29 = schlegel_dng29.
Proof. reflexivity. Qed.
Lemma ok_dng29_banc : banc_dng29 = schlegel_dng29.
Proof. reflexivity. Qed.
Lemma ok_dng29_meta : meta_dng29 = schlegel_dng29.
Proof. reflexivity. Qed.
Lemma ok_hemibrain_dng29 : hemibrain_dng29 = 0.
Proof. reflexivity. Qed.
Lemma ok_easy : easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n.
Proof. reflexivity. Qed.
Lemma ok_challenge : challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n.
Proof. reflexivity. Qed.
Lemma ok_use : use_correct + use_wrong = use_n.
Proof. reflexivity. Qed.
Lemma ok_leftover : leftover_mapped = leftover_n.
Proof. reflexivity. Qed.
Lemma ok_dng29_male_desc : Nat.ltb 1000 dng29_male_desc_milli = true.
Proof. reflexivity. Qed.
Lemma ok_dng29_banc_desc : Nat.ltb 1000 dng29_banc_desc_milli = true.
Proof. reflexivity. Qed.
Lemma ok_kcgm_male : Nat.leb kcgm_male_vm_milli 1000 = true.
Proof. reflexivity. Qed.
Lemma ok_kcgm_banc : Nat.leb kcgm_banc_vm_milli 1000 = true.
Proof. reflexivity. Qed.
Lemma ok_l5_male : Nat.leb l5_male_vm_milli 1000 = true.
Proof. reflexivity. Qed.
Lemma ok_l5_banc : Nat.leb l5_banc_vm_milli 1000 = true.
Proof. reflexivity. Qed.
Lemma ok_early : Nat.ltb 1000 early_vm_milli = true.
Proof. reflexivity. Qed.
Lemma ok_h07b : Nat.ltb 1000 h07b_vm_milli = true.
Proof. reflexivity. Qed.
Lemma ok_mbp3 : Nat.leb mbp3_vm_milli 1000 = true.
Proof. reflexivity. Qed.
Lemma ok_resource : Nat.leb resource_reached trials = true.
Proof. reflexivity. Qed.
Lemma ok_guards_on : guard_jo = 1 /\ guard_vnc = 1 /\ guard_gaba = 1.
Proof. repeat split; reflexivity. Qed.
Lemma ok_guards_off : guard_courtship = 0 /\ guard_aggression = 0 /\ guard_fru_dsx = 0.
Proof. repeat split; reflexivity. Qed.
