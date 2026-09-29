---- MODULE FlySpine ----
EXTENDS Naturals

\* Fly obligation routing. Pin AEB2AD. 0 free parameters.
\* Courtship stays off. A missing measurement is not filled with a count.
\* Synapses are not invented.

VARIABLES courtship, freeParams, inventedSynapse, missingFile

TypeOK ==
  /\ courtship \in BOOLEAN
  /\ freeParams \in Nat
  /\ inventedSynapse \in BOOLEAN
  /\ missingFile \in BOOLEAN

Init ==
  /\ courtship = FALSE
  /\ freeParams = 0
  /\ inventedSynapse = FALSE
  /\ missingFile = TRUE

ObserveAllowed ==
  /\ UNCHANGED <<courtship, freeParams, inventedSynapse, missingFile>>

Next == ObserveAllowed

Spec == Init /\ [][Next]_<<courtship, freeParams, inventedSynapse, missingFile>>

CourtshipOff == courtship = FALSE
ZeroFreeParams == freeParams = 0
NeverInventSynapse == inventedSynapse = FALSE
MissingStaysMissing == missingFile = TRUE

====
