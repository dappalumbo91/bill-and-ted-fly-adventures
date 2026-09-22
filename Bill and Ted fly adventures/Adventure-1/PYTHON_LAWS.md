# Python laws

Pin AEB2AD. 0 free parameters. Measured edges unchanged. Loop horizon 11, which is round(φ^5). The program runs in the restricted Python sandbox on the language splice.

The laws are a value, a fold, a name binding, a larger-of choice, a count, and a function. A function is the fold with a hole. Applying it twice is that same function used again. The sandbox is what produces the number. The sentence does not carry the answer.

One plus one is `(1 + 1)`. One plus one plus one is `((1 + 1) + 1)`. The second program is the first program with one more sum. Add-and uses that same fold: add 1 and 1 writes the same source as one plus one.

```
def step(n):
    return n + 1
step(step(5))
```

That run returns 7. Three applications of the same function, `step(step(step(2)))`, return 5.

A sentence that does not compose stays a leftover. `plus plus one` has no value where a value has to be. `import` and `open` stay outside the sandbox. A courtship name is DENY. Sort has no law here. A count with more than 11 steps is a refusal. The result stays unset.

## Taught

Correct **7** / **7**, wrong **0**, leftover **0**.

| id | status | want | sandbox gave | law | program |
|---|---|---|---|---|---|
| `sum-2` | correct | 2 | 2 | fold | `(1 + 1)` |
| `sum-3` | correct | 3 | 3 | fold | `((1 + 1) + 1)` |
| `add-3` | correct | 15 | 15 | fold | `((4 + 9) + 2)` |
| `bind` | correct | 12 | 12 | bind | `x = (3 + 4) / (x + 5)` |
| `larger` | correct | 6 | 6 | larger | `(6 if 6 > 2 else 2)` |
| `count` | correct | 4 | 4 | count | `k = 0 / while k < 4: /     k = k + 1 / k` |
| `fn-twice` | correct | 7 | 7 | define+apply | `def step(n): /     return n + 1 / step(step(5))` |

## New sentences

Correct **15** / **15**, wrong **0**, leftover **0**.

| id | status | want | sandbox gave | law | program |
|---|---|---|---|---|---|
| `fresh-sum-4` | correct | 4 | 4 | fold | `(((1 + 1) + 1) + 1)` |
| `fresh-words` | correct | 6 | 6 | fold | `((2 + 2) + 2)` |
| `fresh-add-5` | correct | 5 | 5 | fold | `((((1 + 1) + 1) + 1) + 1)` |
| `fresh-mix` | correct | 1 | 1 | fold | `((1 + 1) - 1)` |
| `fresh-minus` | correct | 2 | 2 | fold | `((5 - 2) - 1)` |
| `fresh-tie` | correct | 9 | 9 | larger | `(9 if 9 > 9 else 9)` |
| `fresh-larger-sum` | correct | 2 | 2 | larger | `((1 + 1) if (1 + 1) > 2 else 2)` |
| `fresh-count-11` | correct | 11 | 11 | count | `k = 0 / while k < 11: /     k = k + 1 / k` |
| `fresh-count-from` | correct | 7 | 7 | count | `k = 3 / while k < 7: /     k = k + 1 / k` |
| `fresh-bind` | correct | 8 | 8 | bind | `y = (10 - 3) / (y + 1)` |
| `fresh-grow` | correct | 7 | 7 | define+apply | `def grow(n): /     return n + 3 / grow(grow(1))` |
| `fresh-thrice` | correct | 5 | 5 | define+apply | `def step(n): /     return n + 1 / step(step(step(2)))` |
| `fresh-apply-sum` | correct | 3 | 3 | define+apply | `def step(n): /     return n + 1 / step((1 + 1))` |
| `fresh-back` | correct | 3 | 3 | define+apply | `def back(n): /     return n - 1 / back(back(5))` |
| `fresh-apply-11` | correct | 11 | 11 | define+apply | `def step(n): /     return n + 1 / step(step(step(step(step(step(step(step(step(step(step(0)))))))))))` |

## Refusals

Correct **12** / **12**, wrong **0**, leftover **0**.

| id | status | want | sandbox gave | law | program |
|---|---|---|---|---|---|
| `ill-plus` | correct | None | None | does not compose | `` |
| `ill-mid` | correct | None | None | does not compose | `` |
| `ill-add` | correct | None | None | does not compose | `` |
| `ill-tail` | correct | None | None | does not compose | `` |
| `import` | correct | None | forbid Import | forbid Import | `` |
| `open` | correct | None | forbid call | forbid call | `` |
| `court` | correct | None | DENY | DENY | `` |
| `define-court` | correct | None | DENY | DENY | `` |
| `sort` | correct | None | None | does not compose | `` |
| `count-12` | correct | None | None | horizon | `` |
| `apply-12` | correct | None | None | horizon | `` |
| `unbound` | correct | None | None | unbound | `` |

## Sandbox already in the simulation

The earlier worksheet still matches: **7** / **7**. A defined function `step(step(1))` returns **3**. Courtship stays DENY. Import and open stay refused.

Same law held: **True**. Horizon refusal held: **True**.
