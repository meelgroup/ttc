# Building ttc from source

The released binary archives (see the [Releases page](https://github.com/meelgroup/ttc/releases))
are the recommended way to run `ttc`. This document covers the from-source build
for contributors and for platforms without a prebuilt archive.

## System requirements

Linux:
```sh
sudo apt install cmake build-essential curl \
  libeigen3-dev libboost-dev libboost-program-options-dev \
  libgmp-dev libmpfr-dev \
  autoconf automake libtool pkg-config
```

macOS:
```sh
brew install cmake curl eigen boost gmp mpfr \
  autoconf automake libtool pkg-config
```

Python 3.11+.

## Clone and build

```sh
git clone --recurse-submodules https://github.com/meelgroup/ttc
cd ttc
pip install -r requirements.txt
bash configure.sh
```

`configure.sh` builds all C++ dependencies (cvc5, VolEsti, allsat-circuits,
lrslib, cddlib) into `bin/` and `bin/deps/`. Pass `--force` to rebuild a
dependency that is already present.

## Notes on pycddlib

`pycddlib` links against the GMP build of cddlib. The repo builds its own copy
under `bin/deps/cddlib/install`; point `pip` at it so the extension module
finds the right headers and library:

```sh
CDDLIB_PREFIX="$PWD/bin/deps/cddlib/install"
CFLAGS="-I$CDDLIB_PREFIX/include -I$CDDLIB_PREFIX/include/cddlib" \
LDFLAGS="-L$CDDLIB_PREFIX/lib -Wl,-rpath,$CDDLIB_PREFIX/lib" \
  pip install -r requirements.txt
```

On macOS add `-I$(brew --prefix gmp)/include` / `-L$(brew --prefix gmp)/lib`
to `CFLAGS`/`LDFLAGS` and `ARCHFLAGS="-arch $(uname -m)"` to the command.

## Running

```sh
./ttc example/box_or_lra.smt2
```

If `pycddlib` was built against the in-tree cddlib you may need to expose the
library path at runtime:

```sh
export LD_LIBRARY_PATH="$PWD/bin/deps/cddlib/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
# macOS
export DYLD_LIBRARY_PATH="$PWD/bin/deps/cddlib/install/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
```
