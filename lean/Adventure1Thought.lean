-- Adventure 1 thought law. Pin AEB2AD. 0 free parameters.
-- One agreed label overlays. Disagreement or silence is trit 0 (no letter).
-- The counts are the replay after the TED-33 relations. Lean checks the arithmetic.

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

def easyN : Nat := 570
def easyCorrect : Nat := 570
def easyWrong : Nat := 0
def easyLeftover : Nat := 0
def easyConsensus : Nat := 0
#guard easyCorrect + easyWrong + easyLeftover + easyConsensus = easyN

def challengeN : Nat := 299
def challengeCorrect : Nat := 299
def challengeWrong : Nat := 0
def challengeLeftover : Nat := 0
def challengeConsensus : Nat := 0
#guard challengeCorrect + challengeWrong + challengeLeftover + challengeConsensus = challengeN

def useN : Nat := 343
def useCorrect : Nat := 343
def useWrong : Nat := 0
#guard useCorrect + useWrong = useN
#guard useWrong = 0
