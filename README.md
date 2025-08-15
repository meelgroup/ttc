# TTC: Toolbox for Theory Counting

Volume computation for SMT LRA formulas. Corresponding paper from [KR 2025](https://arxiv.org/abs/2508.09934).

*This repository provides the reference implementation used in the KR 2025 evaluation; an easily installable release is coming soon.*

## Requirements

- Python
- `lark-parser` library: `pip install lark-parser`

## Usage

1. Save your SMT-LIB 2 constraints to a file (e.g., `input.smt`).
2. Run TTC:
   ```sh
   ./ttc input.smt2
   ```
3. To see various options, run `./ttc --help`.
