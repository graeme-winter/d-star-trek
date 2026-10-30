#!/bin/bash
# Compare two pipeline work directories made by tests/run_pipeline.sh.
#
#   tests/compare_runs.sh REFERENCE_DIR TEST_DIR
#
# Reflection files (.ref) must match byte-for-byte.  Headers (.head) and logs
# (.log) must match after removing run-dependent text: date/time stamps, the
# build date in the version banner, the echoed command line and the directory
# the programs ran from.
# Exits non-zero if anything differs.

set -uo pipefail

if [ $# -ne 2 ]; then
    sed -n '2,8p' "$0"
    exit 2
fi

normalise() {
    # The echoed command line wraps at a width that depends on the length of
    # the program path, so drop it entirely.
    awk '/^Command line:/ {skip = 1; next} skip && /^$/ {skip = 0} !skip' "$1" |
    sed -E \
        -e 's/^DTREK_DATE_TIME=.*$/DTREK_DATE_TIME=<removed>;/' \
        -e 's/Date: .* Time: .* Elapsed: .*/Date: <removed>/' \
        -e 's/^(d\*TREK version [^ ]+) -- .*/\1 -- <removed>/' \
        -e 's#(^| )/[^ ]*/(dt[a-z0-9]+|sca2dtrek)( |$)#\1\2\3#g' 
}

status=0
for a in "$1"/*; do
    name=$(basename "$a")
    b="$2/$name"
    if [ ! -e "$b" ]; then
        echo "MISSING $name"
        status=1
        continue
    fi
    case "$name" in
        *.head|*.log)
            if ! diff -q <(normalise "$a") <(normalise "$b") > /dev/null; then
                echo "DIFFER  $name"
                diff <(normalise "$a") <(normalise "$b") | head -10
                status=1
            fi
            ;;
        *)
            if ! cmp -s "$a" "$b"; then
                echo "DIFFER  $name"
                status=1
            fi
            ;;
    esac
done
for b in "$2"/*; do
    [ -e "$1/$(basename "$b")" ] || { echo "EXTRA   $(basename "$b")"; status=1; }
done
[ $status -eq 0 ] && echo "IDENTICAL: $1 $2"
exit $status
