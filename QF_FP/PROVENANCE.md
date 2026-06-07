# SMT-COMP 2025 — Single Query Track, QF_FP division

The 275 benchmarks selected for the QF_FP division of the SMT-COMP 2025
Single Query Track, extracted from the official results data
(https://github.com/SMT-COMP/smt-comp.github.io, data/results-sq-2025.json.gz)
and copied from the SMT-LIB 2025 release (https://zenodo.org/records/15493090,
QF_FP.tar.zst), preserving the family directory structure.

Selection per the SMT-COMP 2024/2025 rules: non-incremental QF_FP benchmarks,
minus those solved by all solvers in <1s (2018-2023) and over-represented
families, capped per logic. The 40k+ "wintersteiger" correctness tests are all
removed as trivial.
