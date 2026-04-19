# TTC: Toolbox for Theory Counting

Volume computation for SMT LRA formulas. Corresponding paper from [KR 2025](https://arxiv.org/abs/2508.09934).

## Requirements

**System** (Linux/macOS):

- Linux: `cmake build-essential libeigen3-dev libboost-dev libboost-program-options-dev libgmp-dev libmpfr-dev autoconf automake libtool pkg-config`
- macOS: `brew install cmake eigen boost gmp mpfr autoconf automake libtool pkg-config`

**Python 3.11+**

## Install

```sh
git clone --recurse-submodules <repo-url>
cd ttc
pip install -r requirements.txt
bash configure.sh
```

`configure.sh` builds all C++ dependencies (cvc5, VolEsti, allsat-circuits, lrslib) into `bin/`. Skips any binary already present; use `--force` to rebuild.

## Usage

```sh
./ttc example/box_or_lra.smt2
```

Output includes a line of the form:

```
s vol <float>
```

For all options: `./ttc --help`
