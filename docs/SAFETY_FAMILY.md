# Host eval, Python sandbox, safety family (TED-15)

Pin **AEB2AD**. 0 free parameters.

## Why not unrestricted host eval / open Python

Unrestricted `eval`/`exec`/`import os` is an attack on the host, not an FSOT observer. The sandbox is the host eval we run: AST whitelist, no import, no open, no attributes, loop cap \(\varphi^5=11\). Trit coding and sandbox Python take the same worksheet.

Host-eval match **7/7**.

## Safety map — courtship / aggression (T1 off)

Measured, not enabled. *fru*/*dsx* selectors. **pC1** is on both the courtship clip (fru-GAL4) and the aggression opto clip (pC1SS2). Same cells, different observer. If we seed them, they can light motor — that is why default is off.

Mode: **live_T1_off**.

| Seed | n | hop-2 vm | hop-2 desc | If T1 were on |
|------|--:|---------:|-----------:|---------------|
| pC1 | 156 | 1.36 | **30.94** | descending command |
| TN1 | 35 | **10.07** | 1.22 | VNC motor |
| fru/dsx labeled | 5012 | 7.26 | **35.21** | descending command |

That is the safety fact: the family **can drive motor**. Default observer stays off. Language/code still DENY those names.

**33/33**. promotes=True.
