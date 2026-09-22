# Math gaps and the errors they exposed

Pin AEB2AD. 0 free parameters. Measured edges unchanged.

Three results were wrong, not refusals.

- `Simplify: 1/3 * 1/4` reached the integer ALU. Integer division makes 1/3 into 0, so the product was 0. The fraction is 1/12. That is Be Prepared 6.11.
- `What number is 35% of 90?` used whole-number percent and returned 31. Example 6.14 is 31.5.
- `What percent of 80 is 20?` took the numbers in the order written and returned 400. The part is 20 and the whole is 80, so the percent is 25.

The gaps that were still refusals are one-step equations (`2y - 3 = 9`), a whole-number power (`4^5`), a tip, and a sale price after a discount.

## These items

Correct **8** / **8**, wrong **0**, leftover **0**.

| id | status | want | family gave | route |
|---|---|---|---|---|
| `os6-6.11` | correct | 1/12 | 1/12 | fraction_simplify |
| `ex-6.14` | correct | 31.5 | 31.5 | percent_of |
| `ex-6.16` | correct | 48 | 48 | percent_of_what |
| `gap-what-percent` | correct | 25 | 25 | what_percent |
| `gap-linear` | correct | 6 | 6 | solve_linear |
| `gap-power` | correct | 1024 | 1024 | power |
| `gap-tip` | correct | 16 | 16 | tip |
| `gap-sale` | correct | 30 | 30 | sale_price |

## New wordings

Correct **8** / **8**, wrong **0**, leftover **0**.

| id | status | want | family gave | route |
|---|---|---|---|---|
| `fresh-frac` | correct | 3/10 | 3/10 | fraction_simplify |
| `fresh-pct` | correct | 9 | 9 | percent_of |
| `fresh-base` | correct | 30 | 30 | percent_of_what |
| `fresh-wp` | correct | 20 | 20 | what_percent |
| `fresh-lin` | correct | 5 | 5 | solve_linear |
| `fresh-pow` | correct | 64 | 64 | power |
| `fresh-tip` | correct | 5 | 5 | tip |
| `fresh-sale` | correct | 64 | 64 | sale_price |

## Near misses

Correct **6** / **6**, wrong **0**, leftover **0**.

| id | status | want | family gave | route |
|---|---|---|---|---|
| `near-frac-sum` | correct | 7/12 | 7/12 | fraction_simplify |
| `near-pct-part` | correct | 20 | 20 | percent_of |
| `near-lin-plus` | correct | 3 | 3 | solve_linear |
| `near-pow` | correct | 625 | 625 | power |
| `near-discount-amount` | correct | 10 | 10 | discount_amount |
| `near-gallons` | correct | 10 | 10 | is_what_pct |

## Still holding

Chapter 6 Be Prepared **12** / **12**. Earlier new wordings **12** / **12**. Earlier near misses **4** / **4**. OpenStax bank **15** / **15**.
