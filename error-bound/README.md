# Floating-point error-bound benchmarks (crafted)

A small family of `QF_FP` benchmarks that ask, for a numerical kernel `f`:

> **Is there an input in range where computing `f` in `float` (Float32) differs
> from computing it in `double` (Float64) by more than `ε`?**

i.e. each file is satisfiable iff some in-range input drives the single-precision
round-off error above `ε`. **SAT = a witness input** with large round-off — exactly
the kind of question a stochastic-local-search solver answers well, and the
floating-point analogue of the round-off-error analyses done by
[FPTaylor](https://github.com/soarlab/FPTaylor) / FPBench / Daisy / Gappa, a genre
the SMT-COMP `QF_FP` set otherwise lacks.

## Encoding

For inputs `x` (Float32, constrained to the kernel's range):

```
f32 = f(x)                          ; computed entirely in Float32
f64 = f(to_fp64(x))                 ; computed in Float64
err = |to_fp64(f32) - f64|          ; round-off error, measured in double
assert (fp.gt err ε)
```

All operations use `roundNearestTiesToEven`. Constants are `to_fp`-from-decimal
literals. (FPTaylor bounds `double`-vs-`real`; the SMT-feasible analogue here is
`float`-vs-`double`, with `double` as the accurate reference.)

## Kernels and levels

Nine classic FPTaylor kernels, expressions and input ranges transcribed verbatim:
`rigidBody1`, `rigidBody2`, `doppler1`, `verhulst`, `predatorPrey`, `turbine1`,
`sine`, `sqroot`, `sineOrder3`.

Two difficulty levels per kernel (`probe.py` measures the achievable error to set
them):
- **`_easy`** — `ε ≈ median` round-off error (many witnesses).
- **`_hard`** — `ε ≈ p99` (only ~1% of inputs qualify, so the search must find a
  rare input).

→ 18 benchmarks, all **satisfiable**.

## Solver notes

- **fp-sls** solves all 18 (its `sat` is exact-rechecked, so the witnesses are
  sound).
- **cvc5 / z3** decide only the two smallest single-variable kernels in time
  (`verhulst_easy`, `predatorPrey_easy`); the dual Float32+Float64 arithmetic
  bit-blasts too large otherwise. This SLS-vs-complete-solver gap is the point of
  the family.
- Requires `fp.abs` (standard `QF_FP`).

## Reproduce

```sh
python3 gen.py <out-dir>     # regenerate the 18 .smt2 files
python3 probe.py             # measure achievable float-vs-double error per kernel (needs numpy)
```
