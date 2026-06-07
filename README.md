# fp-sls evaluation benchmarks — SMT-COMP 2025 QF_FP (SAT + UNKNOWN)

This directory holds the **151** QF_FP benchmarks used to evaluate `fp-sls`,
together with the labels and provenance needed to reproduce the selection.

```
QF_FP/                  the 151 .smt2 benchmarks, in their SMT-LIB family dirs
QF_FP/status.csv        per-benchmark status (sat | unknown) used for the eval
QF_FP/PROVENANCE.md     where the files came from
removed-unsat.txt       the 124 unsat benchmarks excluded from the eval
README.md               this file
```

## What this set is

It is the **QF_FP division of the SMT-COMP 2025 Single Query Track**, restricted
to the **satisfiable and status-unknown** instances:

| | count |
|---|---|
| Official SMT-COMP 2025 QF_FP single-query benchmarks | **275** |
| – removed: `unsat` | 124 |
| **= kept: `sat` (147) + `unknown` (4)** | **151** |

`fp-sls` is an incomplete, satisfiability-only stochastic local search solver:
it finds models but cannot prove `unsat`. The 124 `unsat` instances are
therefore out of scope and removed; the 4 `unknown` are kept because a model may
exist for them.

## How the 275 were selected (SMT-COMP 2024/2025 rules)

The 275 are the official competition selection, **not** a hand-rolled filter.
The selection rules (stable since SMT-COMP 2019, applied in 2024/2025):

- **non-incremental** benchmarks (this is the Single Query Track);
- **remove every benchmark solved by *all* solvers (incl. non-competing) in
  under 1 second** in the previous year's competition — this is the core rule,
  introduced because ~71% of benchmarks were trivially solved by everyone;
- **cap each division's size** (the upper bound depends on the logic's size),
  selecting randomly with family-diversity weighting from what remains;
- consequently the ~40k trivial "wintersteiger" FP correctness tests are all
  removed (they are solved instantly by every solver).

Sources: SMT-COMP [2019](https://smt-comp.github.io/2019/rules19.pdf) /
[2021](https://smt-comp.github.io/2021/rules.pdf) rules.

## How the sat/unsat/unknown labels were determined

**The labels are the competition's *determined* status — the union over all
sound solvers — not the `:status` annotation inside each `.smt2` file.** A
benchmark is `unsat` if any sound solver proved it `unsat`, `sat` if any solver
returned a (model-backed) `sat`, else `unknown`. We took these from the official
results data (`results-sq-2025.json.gz` in `SMT-COMP/smt-comp.github.io`).

This matters because the embedded file `:status` is often stale. Cross-tabulating
our labels against each file's `(set-info :status …)`:

| our label | file `:status` | count |
|---|---|---|
| sat | sat | 118 |
| **sat** | **unknown** | **29** |
| unknown | unknown | 3 |
| **unknown** | **unsat** | **1** |

30 of 151 differ from the file annotation — e.g. `griggio/fmcad12/sin.c.125`
carries `:status unknown` in the file but is **sat** (modern solvers found a
model in 2025).

## Verification against the official results

Aggregating `results-sq-2025.json.gz` (QF_FP, Single Query Track) confirms the
split and the per-solver numbers (competition budget: 1200 s / ~30 GB):

```
275 benchmarks  →  147 sat / 124 unsat / 4 unknown   (union over sound solvers)

solver        sat  unsat  solved
Bitwuzla      140    115    255
COLIBRI       133     99    232
cvc5          139     91    230
colibri2      117     82    199
Z3-Owl        104     69    173
```

Note `determined-unsat = 124` is the **union**; the best single solver
(Bitwuzla) proved only 115 unsat — the other 9 were proved by COLIBRI/cvc5/
colibri2 on instances Bitwuzla timed out on.

## Caveat on the 4 `unknown`

The 147 `sat` are reliable (a sound solver produced a model). The 4 `unknown`
are genuinely undetermined, and one of them —
`schanda/spark/angle_between_1.smt2` — carries an (unverified) `:status unsat`
file annotation, so it may in fact be unsat (in which case no satisfiability-only
solver can solve it). Treat the 4 unknowns as "possibly satisfiable," not as
known sat targets.

## Sources

- Benchmark files: SMT-LIB 2025 release, `QF_FP.tar.zst`
  (<https://zenodo.org/records/15493090>).
- Selection + status: SMT-COMP 2025 Single Query results data
  (`results-sq-2025.json.gz`, <https://github.com/SMT-COMP/smt-comp.github.io>);
  results page <https://smt-comp.github.io/2025/results/qf_fp-single-query/>.
- SMT-COMP 2025 benchmark archive: <https://zenodo.org/records/16887742>.
