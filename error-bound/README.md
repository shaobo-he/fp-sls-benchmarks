# Floating-point error-bound benchmarks (crafted)

A family of `QF_FP` benchmarks that ask, for a numerical kernel `f`:

> **Is there an input in range where computing `f` in `float` (Float32) differs
> from computing it in `double` (Float64) by more than `ε`?**

Each file is satisfiable iff some in-range input drives the single-precision
round-off error above `ε` — **SAT = a witness input** with large round-off. This
is the floating-point analogue of the round-off-error analyses done by
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

All ops use `roundNearestTiesToEven`. **Constants are pure FP bit patterns**
(`((_ to_fp eb sb) (_ bv<ieee-bits> N))`, like the SMT-COMP griggio benchmarks) —
*not* `to_fp`-from-decimal, which pulls in the Real sort and is non-portable
(cvc5 rejects negative/integer reals; some solvers need preprocessing).

## Kernels and ε levels

Nine FPTaylor kernels (expressions + ranges transcribed verbatim): `rigidBody1`,
`rigidBody2`, `doppler1`, `verhulst`, `predatorPrey`, `turbine1`, `sine`,
`sqroot`, `sineOrder3`.

Three difficulty levels per kernel (`probe.py` measures the achievable error):
- **`_easy`** — `ε ≈ median` round-off error (many witnesses).
- **`_hard`** — `ε ≈ p99` (≈1% of inputs qualify).
- **`_vhard`** — `ε ≈ 0.99×max` (the witness is a near-worst-case input — a
  needle, especially for the 3-variable kernels).

→ 27 benchmarks, all **satisfiable**.

## Reproduce

```sh
python3 gen.py <out-dir>        # regenerate the 27 .smt2 files
python3 probe.py 20000000      # measure achievable float-vs-double error (needs numpy)
```
