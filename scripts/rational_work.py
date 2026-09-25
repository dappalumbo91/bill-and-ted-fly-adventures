#!/usr/bin/env python3
"""Rational procedures for decimals, fractions, one-step equations, ratios, and rates.

Whole-number trit expressions stay on the integer ALU. A decimal point is not a
balanced-ternary digit, so these prompts used to refuse. The operation is the
sentence shape. The same procedure has to work on a new wording.
"""
from __future__ import annotations

import runio
runio.install()

import re
from fractions import Fraction


def _dec(text: str) -> Fraction:
    """Exact decimal. Fraction('0.62') is 31/50, not a binary float."""
    return Fraction(text)


def _number(fr: Fraction):
    if fr.denominator == 1:
        return int(fr)
    return float(fr)


def _ratio_text(fr: Fraction) -> str:
    return f"{fr.numerator}/{fr.denominator}"


class _Rat:
    def __init__(self, src: str):
        self.s = src.replace(" ", "")
        self.i = 0

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def parse(self) -> Fraction:
        value = self.add()
        if self.i != len(self.s):
            raise ValueError("trailing")
        return value

    def add(self) -> Fraction:
        value = self.mul()
        while self.peek() in ("+", "-"):
            op = self.peek()
            self.i += 1
            right = self.mul()
            value = value + right if op == "+" else value - right
        return value

    def mul(self) -> Fraction:
        value = self.unary()
        while True:
            op = self.peek()
            if op in ("*", "/"):
                self.i += 1
                right = self.unary()
                if op == "/" and right == 0:
                    raise ZeroDivisionError
                value = value * right if op == "*" else value / right
            elif op == "(" or op.isdigit():
                value = value * self.unary()
            else:
                return value

    def unary(self) -> Fraction:
        if self.peek() == "-":
            self.i += 1
            return -self.unary()
        if self.peek() == "+":
            self.i += 1
            return self.unary()
        return self.primary()

    def primary(self) -> Fraction:
        if self.peek() == "(":
            self.i += 1
            value = self.add()
            if self.peek() != ")":
                raise ValueError("paren")
            self.i += 1
            return value
        return self.number()

    def number(self) -> Fraction:
        start = self.i
        while self.peek().isdigit():
            self.i += 1
        if self.peek() == ".":
            self.i += 1
            if not self.peek().isdigit():
                raise ValueError("decimal")
            while self.peek().isdigit():
                self.i += 1
        if self.i == start:
            raise ValueError("number")
        return _dec(self.s[start : self.i])


def rational_expr(src: str) -> Fraction:
    return _Rat(src).parse()


def rational_work(prompt: str):
    """Return (value, how) or None when this sentence is not one of these operations."""
    t = prompt.lower().replace("−", "-").replace("–", "-").replace(",", "")

    ratio = re.search(r"ratio of\s+(-?\d+)\s+to\s+(-?\d+)", t)
    if ratio and "write" not in t:
        num, den = int(ratio.group(1)), int(ratio.group(2))
        if den == 0:
            return None
        return _ratio_text(Fraction(num, den)), "ratio"

    as_decimal = re.search(r"write\s+(-?\d+)\s*/\s*(-?\d+)\s+as a decimal", t)
    if as_decimal:
        den = int(as_decimal.group(2))
        if den == 0:
            return None
        return _number(Fraction(int(as_decimal.group(1)), den)), "fraction_to_decimal"

    as_fraction = re.search(r"write\s+(-?\d+\.\d+)\s+as a fraction", t)
    if as_fraction:
        return _ratio_text(_dec(as_fraction.group(1))), "decimal_to_fraction"

    keep_fraction = re.search(r"write\s+(-?\d+)\s*/\s*(-?\d+)\s+as a fraction", t)
    if keep_fraction:
        den = int(keep_fraction.group(2))
        if den == 0:
            return None
        return _ratio_text(Fraction(int(keep_fraction.group(1)), den)), "fraction_lowest"

    keep_decimal = re.search(r"write\s+(-?\d+\.\d+)\s+as a decimal", t)
    if keep_decimal:
        return _number(_dec(keep_decimal.group(1))), "decimal_unchanged"

    of_unknown = re.search(
        r"(-?\d+)\s*/\s*(-?\d+)\s+of\s+[a-z]\s+is\s+(-?\d+(?:\.\d+)?)",
        t,
    )
    if of_unknown:
        num, den, total = int(of_unknown.group(1)), int(of_unknown.group(2)), _dec(of_unknown.group(3))
        if num == 0 or den == 0:
            return None
        return _number(total / Fraction(num, den)), "fraction_of_unknown"

    coeff_eq = re.search(
        r"(-?\d+(?:\.\d+)?)\s*=\s*(-?\d+(?:\.\d+)?)\s*\*?\s*[a-z]\b",
        t,
    )
    if coeff_eq:
        left, coeff = _dec(coeff_eq.group(1)), _dec(coeff_eq.group(2))
        if coeff == 0:
            return None
        return _number(left / coeff), "solve_coeff"

    var_coeff = re.search(
        r"(-?\d+(?:\.\d+)?)[a-z]\s*=\s*(-?\d+(?:\.\d+)?)",
        t,
    )
    if var_coeff:
        coeff, right = _dec(var_coeff.group(1)), _dec(var_coeff.group(2))
        if coeff == 0:
            return None
        return _number(right / coeff), "solve_var_coeff"

    var_div = re.search(
        r"[a-z]\s*/\s*(-?\d+(?:\.\d+)?)\s*=\s*(-?\d+(?:\.\d+)?)",
        t,
    )
    if var_div:
        den, right = _dec(var_div.group(1)), _dec(var_div.group(2))
        if den == 0:
            return None
        return _number(den * right), "solve_var_div"

    percent_of = re.search(
        r"what percent of\s+(-?\d+(?:\.\d+)?)\s+is\s+(-?\d+(?:\.\d+)?)",
        t,
    )
    if percent_of:
        whole, part = _dec(percent_of.group(1)), _dec(percent_of.group(2))
        if whole == 0:
            return None
        return _number(part / whole * 100), "what_percent"

    is_percent_of = re.search(
        r"(-?\d+(?:\.\d+)?)\s+is\s+(-?\d+(?:\.\d+)?)\s*%\s+of",
        t,
    )
    if is_percent_of:
        part, pct = _dec(is_percent_of.group(1)), _dec(is_percent_of.group(2))
        if pct == 0:
            return None
        return _number(part / (pct / 100)), "percent_of_what"

    number_is_percent = re.search(
        r"(?:what number is|how much is)\s+(-?\d+(?:\.\d+)?)\s*%\s+of\s+(-?\d+(?:\.\d+)?)",
        t,
    )
    if number_is_percent:
        pct, base = _dec(number_is_percent.group(1)), _dec(number_is_percent.group(2))
        return _number(base * pct / 100), "percent_of"

    bare_percent = re.search(
        r"(-?\d+(?:\.\d+)?)\s*%\s+of\s+(-?\d+(?:\.\d+)?)",
        t,
    )
    if bare_percent and "what percent" not in t:
        pct, base = _dec(bare_percent.group(1)), _dec(bare_percent.group(2))
        if "discount" in t and ("sale price" in t or "pay" in t):
            return _number(base * (100 - pct) / 100), "sale_price"
        if "how much is the discount" in t or "discount amount" in t:
            return _number(base * pct / 100), "discount_amount"
        if "tip" in t:
            return _number(base * pct / 100), "tip"
        return _number(base * pct / 100), "percent_of"

    linear = re.search(
        r"(-?\d+)\s*([a-z])\s*([+-])\s*(-?\d+)\s*=\s*(-?\d+)",
        t,
    )
    if not linear:
        linear = re.search(
            r"\b([a-z])\s*([+-])\s*(-?\d+)\s*=\s*(-?\d+)",
            t,
        )
        if linear:
            coeff = Fraction(1)
            var_op, const, right = linear.group(2), _dec(linear.group(3)), _dec(linear.group(4))
            signed = const if var_op == "+" else -const
            return _number((right - signed) / coeff), "solve_linear"
        linear = None
    if linear and linear.lastindex == 5:
        coeff = _dec(linear.group(1))
        var_op, const, right = linear.group(3), _dec(linear.group(4)), _dec(linear.group(5))
        if coeff == 0:
            return None
        signed = const if var_op == "+" else -const
        return _number((right - signed) / coeff), "solve_linear"

    money = re.search(r"(\d+(?:\.\d+)?)\s+dollars", t)
    pct_word = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
    if money and pct_word:
        base, pct = _dec(money.group(1)), _dec(pct_word.group(1))
        if "discount" in t and ("sale price" in t or "pay" in t):
            return _number(base * (100 - pct) / 100), "sale_price"
        if "how much is the discount" in t or "discount amount" in t:
            return _number(base * pct / 100), "discount_amount"
        if "tip" in t:
            return _number(base * pct / 100), "tip"

    power = re.search(r"(-?\d+)\s*\^\s*(\d+)", t)
    if power and "simplify" in t:
        exp = int(power.group(2))
        if 0 <= exp <= 12:
            return int(power.group(1)) ** exp, "power"

    miles = re.search(r"(\d+(?:\.\d+)?)\s+miles\s+in\s+(\d+(?:\.\d+)?)\s+hours", t)
    if miles:
        dist, hours = _dec(miles.group(1)), _dec(miles.group(2))
        if "how many miles" in t:
            return _number(dist), "miles_stated"
        if "how many hours" in t:
            return _number(hours), "hours_stated"
        if hours == 0:
            return None
        if "rate" in t or "per hour" in t:
            return _number(dist / hours), "unit_rate"

    if "through multiplication" in t or "through division" in t:
        head = re.split(r"through (?:multiplication|division)", t, maxsplit=1)[0]
        expr = re.sub(r"^.*\bsolve\s+", "", head).strip()
    elif "simplify:" in t:
        expr = t.split("simplify:", 1)[1].strip()
    else:
        return None
    expr = expr.replace("×", "*").replace("·", "*").replace("÷", "/").strip(" .")
    if not re.search(r"\d", expr):
        return None
    if "." not in expr and "(" not in expr:
        return None
    try:
        return _number(rational_expr(expr)), "rational_expr"
    except (ValueError, ZeroDivisionError):
        return None
