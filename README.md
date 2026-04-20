# TTC: Toolbox for Theory Counting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/meelgroup/ttc/actions/workflows/ci.yml/badge.svg)](https://github.com/meelgroup/ttc/actions/workflows/ci.yml)


`ttc` is a volume computation for SMT (LRA) formulas. Given an LRA formula, `ttc` returns the volume of the solution space with $(\varepsilon,\delta)$-guarantees. Find more details in our [KR 2025 paper](https://arxiv.org/abs/2508.09934).

## Building

**Install Requirements**

Linux:
```
sudo apt install cmake build-essential curl libeigen3-dev libboost-dev libboost-program-options-dev libgmp-dev libmpfr-dev autoconf automake libtool pkg-config
```
macOS:
```
brew install cmake curl eigen boost gmp mpfr autoconf automake libtool pkg-config
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

The expected input format is the [SMT-LIB2](https://smtlib.cs.uiowa.edu/language.shtml) format. The tool supports the theory of linear real arithmetic (QF_LRA). See `example` directory for some examples.

```sh
./ttc example/box_or_lra.smt2
```

Output includes a line of the form:

```
s vol <float>
```

For all options: `./ttc --help`


### Guarantees
`ttc` provides so-called "PAC", or Probably Approximately Correct, guarantees. The system guarantees that the solution found is within a certain tolerance (called "epsilon") with a certain probability (called "delta"). The default tolerance and probability, i.e. epsilon and delta values, are set to 0.8 and 0.2, respectively. Both values are configurable.

### Issues, questions, bugs, etc.
Please click on "issues" at the top and [create a new issue](https://github.com/meelgroup/ttc/issues/new).

## How to Cite

This work is by Arijit Shaw, Uddalok Sarkar, and Kuldeep S. Meel, as [published in KR-25](https://arxiv.org/abs/2508.09934).

The benchmarks used in our evaluation can be found [here](https://zenodo.org/records/16782811).
