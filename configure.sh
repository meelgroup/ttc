#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"
DEPS_DIR="$BIN_DIR/deps"
NPROC=10
FORCE=0

for arg in "$@"; do
  [[ "$arg" == "--force" ]] && FORCE=1
done

need_build() {
  local bin="$BIN_DIR/$1"
  [[ "$FORCE" == 1 ]] && return 0
  [[ -e "$bin" ]] && echo "  -> $1 already exists, skipping (use --force to rebuild)" && return 1
  return 0
}

echo "=== Building dependencies ==="

# --- cddlib (GMP version) ---
CDDLIB_SRC="$DEPS_DIR/cddlib"
CDDLIB_PREFIX="$CDDLIB_SRC/install"
CDDLIB_LIB="$CDDLIB_PREFIX/lib/libcddgmp.a"
if [[ "$FORCE" == 1 ]] || [[ ! -f "$CDDLIB_LIB" ]]; then
  echo ""
  echo "--- Building cddlib (GMP version) ---"
  (cd "$CDDLIB_SRC" && autoreconf -i && ./configure --prefix="$CDDLIB_PREFIX" && make -j"$NPROC" install)
  echo "  -> cddlib installed to $CDDLIB_PREFIX"
else
  echo "  -> cddlib already built, skipping"
fi

# --- VolEsti (examples/volume) ---
if need_build volume || need_build sample; then
  echo ""
  echo "--- Building VolEsti (volume + sample) ---"
  VOLESTI_SRC="$DEPS_DIR/VolEsti/examples/volume"
  VOLESTI_BUILD="$VOLESTI_SRC/build"
  LPSOLVE_DEPS="$DEPS_DIR/VolEsti/external/_deps"

  # Reuse lp_solve source from a previous build to avoid re-downloading
  if [[ ! -f "$LPSOLVE_DEPS/lpsolve-src/lpsolve.h" ]]; then
    cached="$DEPS_DIR/VolEsti/external/_deps/lpsolve-src"
    if [[ -f "$cached/lpsolve.h" ]]; then
      echo "  -> Seeding lp_solve source from $cached"
      mkdir -p "$LPSOLVE_DEPS/lpsolve-src"
      cp -a "$cached/." "$LPSOLVE_DEPS/lpsolve-src/"
    fi
  fi

  # Clean stale build dir if lp_solve wasn't seeded in the previous run
  if [[ -d "$VOLESTI_BUILD" ]] && \
     grep -q "FATAL_ERROR\|lpsolve failed" "$VOLESTI_BUILD/CMakeFiles/CMakeError.log" 2>/dev/null; then
    echo "  -> Cleaning stale VolEsti build dir"
    rm -rf "$VOLESTI_BUILD"
  fi

  mkdir -p "$VOLESTI_BUILD"
  cmake -S "$VOLESTI_SRC" -B "$VOLESTI_BUILD" -DCMAKE_BUILD_TYPE=Release -Wno-dev \
    -DCDDLIB="$CDDLIB_LIB" \
    -DCMAKE_CXX_FLAGS="-I$CDDLIB_PREFIX/include" \
    -DCMAKE_C_FLAGS="-I$CDDLIB_PREFIX/include"
  cmake --build "$VOLESTI_BUILD" -j"$NPROC"
  install -m 755 "$VOLESTI_BUILD/volume" "$BIN_DIR/volume"
  install -m 755 "$VOLESTI_BUILD/sample" "$BIN_DIR/sample"
  echo "  -> volume, sample copied to bin/"
fi

# --- allsat-circuits (hall_tool) ---
if need_build hall_tool; then
  echo ""
  echo "--- Building allsat-circuits (hall_tool) ---"
  ALLSAT_SRC="$DEPS_DIR/allsat-circuits"
  ALLSAT_BUILD="$ALLSAT_SRC/build"
  git -C "$ALLSAT_SRC" submodule update --init --recursive
  mkdir -p "$ALLSAT_BUILD"
  cmake -S "$ALLSAT_SRC" -B "$ALLSAT_BUILD" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$ALLSAT_BUILD" -j"$NPROC"
  install -m 755 "$ALLSAT_BUILD/hall_tool" "$BIN_DIR/hall_tool"
  echo "  -> hall_tool copied to bin/"
fi

# --- pact / cvc5 ---
if need_build cvc5; then
  echo ""
  echo "--- Building pact (cvc5) ---"
  PACT_DIR="$DEPS_DIR/pact"
  (cd "$PACT_DIR" && ./configure.sh --auto-download --tracing)
  PACT_BUILD="$PACT_DIR/build"
  make -j"$NPROC" -C "$PACT_BUILD"
  install -m 755 "$PACT_BUILD/bin/cvc5" "$BIN_DIR/cvc5"
  echo "  -> cvc5 copied to bin/"
fi

# --- upstream-lrslib (lrs) ---
if need_build lrs; then
  echo ""
  echo "--- Building upstream-lrslib (lrs) ---"
  LRS_DIR="$DEPS_DIR/upstream-lrslib"
  # lrslong.c / lrsgmp.c / lrsmp.c live in lrsarith-011/ but Makefile.am expects them at root
  for f in lrslong.c lrslong.h lrsgmp.c lrsgmp.h lrsmp.c lrsmp.h; do
    [[ -e "$LRS_DIR/$f" ]] || ln -s "lrsarith-011/$f" "$LRS_DIR/$f"
  done
  (cd "$LRS_DIR" && autoreconf -i && ./configure && make -j"$NPROC" lrs)
  install -m 755 "$LRS_DIR/lrs" "$BIN_DIR/lrs"
  echo "  -> lrs copied to bin/"
fi

echo ""
echo "=== All dependencies built successfully ==="
