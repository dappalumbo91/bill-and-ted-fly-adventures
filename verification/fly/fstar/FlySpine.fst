module FlySpine

(* Fly obligation spine. Generated. Pin AEB2AD. *)

let free_parameters : nat = 0
let phi_milli : nat = 1618
let inv_phi_milli : nat = 618
let schlegel_n : nat = 139248
let schlegel_dng29 : nat = 2
let schlegel_jo : nat = 1104
let meta_n : nat = 144837
let meta_dng29 : nat = 2
let meta_jo : nat = 1107
let jo_only_meta : nat = 3
let jo_only_tsv : nat = 0
let male_dng29 : nat = 2
let male_jo : nat = 672
let male_traced : nat = 165122
let banc_dng29 : nat = 2
let banc_jo : nat = 1198
let hemibrain_dng29 : nat = 0
let hemibrain_jo : nat = 78
let hemibrain_typed : nat = 22704
let male_neurons : nat = 165122
let male_gaba : nat = 22055
let male_edges : nat = 25563197
let banc_neurons : nat = 175401
let inventory_n : nat = 139248
let easy_n : nat = 570
let easy_correct : nat = 570
let easy_wrong : nat = 0
let easy_leftover : nat = 0
let easy_consensus : nat = 0
let challenge_n : nat = 299
let challenge_correct : nat = 299
let challenge_wrong : nat = 0
let challenge_leftover : nat = 0
let challenge_consensus : nat = 0
let use_n : nat = 343
let use_correct : nat = 343
let use_wrong : nat = 0
let leftover_n : nat = 35
let leftover_mapped : nat = 35
let guard_jo : nat = 1
let guard_vnc : nat = 1
let guard_gaba : nat = 1
let guard_courtship : nat = 0
let guard_aggression : nat = 0
let guard_fru_dsx : nat = 0
let trials : nat = 3
let resource_reached : nat = 2
let measured_w_changed : nat = 0
let dng29_male_desc_milli : nat = 9204
let dng29_male_vm_milli : nat = 2088
let dng29_banc_desc_milli : nat = 7813
let dng29_banc_vm_milli : nat = 5827
let kcgm_male_desc_milli : nat = 53
let kcgm_male_vm_milli : nat = 0
let kcgm_banc_desc_milli : nat = 214
let kcgm_banc_vm_milli : nat = 0
let l5_male_desc_milli : nat = 1916
let l5_male_vm_milli : nat = 1
let l5_banc_desc_milli : nat = 3528
let l5_banc_vm_milli : nat = 0
let early_vm_milli : nat = 24254
let h07b_vm_milli : nat = 27566
let mbp3_vm_milli : nat = 0
let early_n : nat = 7890
let h07b_n : nat = 954
let mbp3_n : nat = 1038

let _ = assert (free_parameters = 0)
let _ = assert (meta_jo = schlegel_jo + jo_only_meta)
let _ = assert (jo_only_tsv = 0)
let _ = assert (inventory_n = schlegel_n)
let _ = assert (male_dng29 = schlegel_dng29)
let _ = assert (banc_dng29 = schlegel_dng29)
let _ = assert (meta_dng29 = schlegel_dng29)
let _ = assert (hemibrain_dng29 = 0)
let _ = assert (easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n)
let _ = assert (challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n)
let _ = assert (use_correct + use_wrong = use_n)
let _ = assert (use_wrong = 0)
let _ = assert (leftover_mapped = leftover_n)
let _ = assert (dng29_male_desc_milli > 1000)
let _ = assert (dng29_banc_desc_milli > 1000)
let _ = assert (kcgm_male_vm_milli <= 1000)
let _ = assert (kcgm_banc_vm_milli <= 1000)
let _ = assert (l5_male_vm_milli <= 1000)
let _ = assert (l5_banc_vm_milli <= 1000)
let _ = assert (early_vm_milli > 1000)
let _ = assert (h07b_vm_milli > 1000)
let _ = assert (mbp3_vm_milli <= 1000)
let _ = assert (guard_jo = 1)
let _ = assert (guard_vnc = 1)
let _ = assert (guard_gaba = 1)
let _ = assert (guard_courtship = 0)
let _ = assert (guard_aggression = 0)
let _ = assert (guard_fru_dsx = 0)
let _ = assert (resource_reached <= trials)
