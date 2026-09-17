#!/usr/bin/env python3
"""Balanced-ternary ALU on native FSOT trits {-1,0,+1}.

No trained weights. Carry is a trit. Integers are finite trit words
(least-significant first). This is the arithmetic the substrate already is.
"""
from __future__ import annotations


def trit(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def consensus(a: int, b: int) -> int:
    return a if a == b else 0


def pair(a: int, b: int) -> int:
    return trit(int(a) * int(b))


def neg(a: int) -> int:
    return trit(-int(a))


def split3(s: int) -> tuple[int, int]:
    """s ∈ [-3, 3] → (digit, carry) in trits.  s = 3·carry + digit."""
    if s >= 2:
        return s - 3, 1
    if s <= -2:
        return s + 3, -1
    return s, 0


def add_digits(a: int, b: int, cin: int = 0) -> tuple[int, int]:
    return split3(int(a) + int(b) + int(cin))


def to_bt(n: int) -> list[int]:
    """n = Σ d_i 3^i with d_i ∈ {-1,0,1}. Least-significant trit first."""
    n = int(n)
    if n == 0:
        return [0]
    digits: list[int] = []
    while n != 0:
        r = n % 3
        if r == 2:
            digits.append(-1)
            n = n // 3 + 1
        else:
            digits.append(int(r))
            n = n // 3
        if len(digits) > 40:
            raise OverflowError("trit word overflow")
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return digits


def from_bt(digits: list[int]) -> int:
    s = 0
    p = 1
    for d in digits:
        s += int(d) * p
        p *= 3
    return s


def pad(a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    n = max(len(a), len(b))
    return a + [0] * (n - len(a)), b + [0] * (n - len(b))


def add_bt(a: list[int], b: list[int]) -> list[int]:
    x, y = pad(a, b)
    out: list[int] = []
    cin = 0
    for da, db in zip(x, y):
        d, cin = add_digits(da, db, cin)
        out.append(d)
    if cin:
        out.append(cin)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def neg_bt(a: list[int]) -> list[int]:
    return [neg(d) for d in a]


def sub_bt(a: list[int], b: list[int]) -> list[int]:
    return add_bt(a, neg_bt(b))


def mul_bt(a: list[int], b: list[int]) -> list[int]:
    acc = [0]
    for i, db in enumerate(b):
        if db == 0:
            continue
        part = list(a) if db > 0 else neg_bt(a)
        acc = add_bt(acc, [0] * i + part)
    return acc


def cmp_bt(a: list[int], b: list[int]) -> int:
    """-1 if a<b, 0 if equal, +1 if a>b."""
    return trit(from_bt(sub_bt(a, b)))


def abs_bt(a: list[int]) -> list[int]:
    return neg_bt(a) if cmp_bt(a, [0]) < 0 else list(a)


def divmod_bt(a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    """Non-negative a, b>0. Repeated trit subtract. Keep |a| modest."""
    if from_bt(b) == 0:
        raise ZeroDivisionError("trit div")
    if cmp_bt(a, [0]) < 0 or cmp_bt(b, [0]) <= 0:
        raise ValueError("divmod_bt wants a≥0, b>0")
    q = [0]
    rem = list(a)
    one = [1]
    guard = 0
    while cmp_bt(rem, b) >= 0:
        rem = sub_bt(rem, b)
        q = add_bt(q, one)
        guard += 1
        if guard > 5000:
            raise OverflowError("divmod_bt too large")
    return q, rem


def fmt_bt(digits: list[int]) -> str:
    g = {1: "1", 0: "0", -1: "T"}
    return "".join(g[int(d)] for d in reversed(digits)) or "0"
