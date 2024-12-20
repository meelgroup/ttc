# TTC: Toolbox for Theory Counting

Count the number of models of a given SMT LIA formula.

## Requirements

- Python
- `lark-parser` library: `pip install lark-parser`
- `cvc5`: Install from [cvc5 internal GitHub](https://github.com/meelgroup/pact) branch `ttc`
- `hall`: Install from [hall GitHub](https://github.com/hall-solver/hall)
- `latte`: Install from [latte GitHub](https://github.com/latte-central/latte)

## Usage

1. Save your SMT-LIB 2 constraints to a file (e.g., `input.smt`).
2. Run TTC:
   ```sh
   ./ttc input.smt2
   ```
3. To see various options, run `./ttc --help`.
