# Shapeshifter

Shapeshifter counts SMT-Lib LIA formulas.

## Requirements

- Python
- `lark-parser` library: `pip install lark-parser`
- `cvc5`: Install from [cvc5 GitHub](https://github.com/meelgroup/cvc5)
- `hall`: Install from [hall GitHub](https://github.com/hall-solver/hall)
- `latte`: Install from [latte GitHub](https://github.com/latte-central/latte)

## Usage

1. Save your SMT-LIB 2 constraints to a file (e.g., `input.smt`).
2. Run the Shapeshifter tool:
   ```sh
   python shapeshifter.py input.smt
   ```