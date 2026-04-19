# TTC: Toolbox for Theory Counting

[![CI](https://github.com/meelgroup/ttc/actions/workflows/ci.yml/badge.svg?branch=devel)](https://github.com/meelgroup/ttc/actions/workflows/ci.yml)

Volume computation for SMT LRA formulas. Corresponding paper from [KR 2025](https://arxiv.org/abs/2508.09934).

## Building

**Install Requirements**

Linux:
```
cmake build-essential libeigen3-dev libboost-dev libboost-program-options-dev libgmp-dev libmpfr-dev autoconf automake libtool pkg-config
```
macOS:
```
brew install cmake eigen boost gmp mpfr autoconf automake libtool pkg-config
```
Make sure you have Python 3.11+.

**Clone and Install**

```sh
git clone --recurse-submodules https://github.com/meelgroup/ttc
cd ttc
pip install -r requirements.txt
bash configure.sh
```

`configure.sh` builds all C++ dependencies (cvc5, VolEsti, allsat-circuits, lrslib) into `bin/`.

## Usage

```sh
./ttc example/box_or_lra.smt2
```

Output includes a line of the form:

```
s vol <float>
```

For all options: `./ttc --help`
