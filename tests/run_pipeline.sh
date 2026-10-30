#!/bin/bash
# Run the d*TREK command-line pipeline on a rotation sweep, non-interactively.
#
#   tests/run_pipeline.sh BINDIR FIRST_IMAGE NIMAGES WORKDIR
#
# e.g. tests/run_pipeline.sh build/bin /data/synth/synth_00001.cbf 60 work
#
# Each step's log is written to WORKDIR/<step>.log; the script stops at the
# first step that fails.  stdin is /dev/null throughout so that programs which
# prompt (dtcell, dtrefine -prompt) take their defaults rather than hang.

set -euo pipefail

if [ $# -ne 4 ]; then
    sed -n '2,10p' "$0"
    exit 2
fi

BIN=$(cd "$1" && pwd)
IMAGE=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
NIMAGES=$3
WORK=$4

mkdir -p "$WORK"
cd "$WORK"

step() {
    local name=$1
    shift
    echo "== $name: $*"
    if ! "$@" < /dev/null > "$name.log" 2>&1; then
        echo "FAILED: $name (see $WORK/$name.log)"
        tail -20 "$name.log"
        exit 1
    fi
}

step find      "$BIN/dtfind" "$IMAGE" -seq 1 "$NIMAGES"
step index     "$BIN/dtindex" "$IMAGE" dtfind.ref
step refine    "$BIN/dtrefine" dtindex.head dtfind.ref +All -go -go -go
step integrate "$BIN/dtintegrate" dtrefine.head -seq 1 "$NIMAGES"
step scale     "$BIN/dtscaleaverage" dtintegrate.head dtprofit.ref

grep -E 'rmsResid \(mm\)' refine.log | tail -1
grep -E '^ (Spacegroup|Total number of reflections|% completeness|Rmerge) ' scale.log
