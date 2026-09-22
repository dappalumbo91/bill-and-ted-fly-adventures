# Chapter 6 refusals, refined

Pin AEB2AD. 0 free parameters. Measured edges unchanged. The integer trit ALU is unchanged. Decimals are not balanced-ternary digits, so a separate rational procedure now handles them.

The Chapter 6 Be Prepared set had been **0** correct, **0** wrong, **12** leftover. Each refusal was a missing operation, or the integer ALU stopping at a decimal point.

| id | now | want | family gave | route | why it had refused |
|---|---|---|---|---|---|
| `os6-6.1` | correct | 33/5 | 33/5 | ratio | No sentence shape for 'ratio of A to B'. The numbers never reached an operation. |
| `os6-6.2` | correct | 0.6 | 0.6 | fraction_to_decimal | No sentence shape for writing a fraction as a decimal. |
| `os6-6.3` | correct | 31/50 | 31/50 | decimal_to_fraction | No sentence shape for writing a decimal as a fraction. |
| `os6-6.4` | correct | 32 | 32 | fraction_of_unknown | '3/4 of x is 24' is a one-step equation. The percent grammar only sees 'N% of M'. |
| `os6-6.5` | correct | 10.71 | 10.71 | rational_expr | The simplify path ran, then the integer ALU stopped at the decimal point. |
| `os6-6.6` | correct | 5 | 5 | solve_coeff | The only solve shape was 'letter - whole = whole'. '3.5 = 0.7n' is a coefficient. |
| `os6-6.7` | correct | 63 | 63 | rational_expr | The prompt says multiplication, not simplify, so the expression was never evaluated. It is also a decimal. |
| `os6-6.8` | correct | 324 | 324 | rational_expr | The prompt says division, not simplify. 12.96 / 0.04 never reached the ALU, and the ALU would have stopped at the point. |
| `os6-6.9` | correct | 75 | 75 | solve_var_coeff | '0.6y = 45' is a coefficient equation. That shape was not in the grammar. |
| `os6-6.10` | correct | 6.67 | 6.67 | solve_var_div | 'n / 1.45 = 4.6' divides the unknown. That shape was not in the grammar. |
| `os6-6.12` | correct | 80 | 80 | solve_var_div | 'x / 4 = 20' is whole numbers the ALU can multiply, but the sentence shape was missing. |
| `os6-6.13` | correct | 12 | 12 | unit_rate | A rate is distance divided by time. The sentence named miles and hours and was not recognized. |

After the rational procedure: correct **12** / **12**, wrong **0**, leftover **0**.

## New wordings

Same operations, different numbers and sentences. Correct **12** / **12**, wrong **0**, leftover **0**.

| id | status | want | family gave | route |
|---|---|---|---|---|
| `fresh-ratio` | correct | 2/3 | 2/3 | ratio |
| `fresh-decimal` | correct | 0.25 | 0.25 | fraction_to_decimal |
| `fresh-fraction` | correct | 3/4 | 3/4 | decimal_to_fraction |
| `fresh-of` | correct | 25 | 25 | fraction_of_unknown |
| `fresh-product` | correct | 10 | 10 | rational_expr |
| `fresh-coeff` | correct | 4 | 4 | solve_coeff |
| `fresh-times` | correct | 20 | 20 | rational_expr |
| `fresh-div` | correct | 21 | 21 | rational_expr |
| `fresh-yc` | correct | 18 | 18 | solve_var_coeff |
| `fresh-over` | correct | 3.5 | 3.5 | solve_var_div |
| `fresh-whole` | correct | 24 | 24 | solve_var_div |
| `fresh-rate` | correct | 15 | 15 | unit_rate |

## Near misses

The other reading of a nearby sentence. Correct **4** / **4**, wrong **0**, leftover **0**.

| id | status | want | family gave | route |
|---|---|---|---|---|
| `near-keep-fraction` | correct | 3/5 | 3/5 | fraction_lowest |
| `near-keep-decimal` | correct | 0.62 | 0.62 | decimal_unchanged |
| `near-miles` | correct | 24 | 24 | miles_stated |
| `near-hours` | correct | 2 | 2 | hours_stated |

## Already taught

OpenStax chapters already in the bank stay exact: **15** / **15**.
