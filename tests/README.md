# Regression testing

The renovation rule is that a change which is not meant to alter behaviour
must not alter output. These scripts check that on a synthetic rotation
sweep.

    # once: write 60 Pilatus 6M miniCBF images (about 370 MB; numpy only)
    python3 tests/make_synthetic_sweep.py /tmp/synth --images 60

    # run the pipeline with a reference build and with the build under test
    tests/run_pipeline.sh reference/bin /tmp/synth/synth_00001.cbf 60 /tmp/run_ref
    tests/run_pipeline.sh build/bin     /tmp/synth/synth_00001.cbf 60 /tmp/run_new

    tests/compare_runs.sh /tmp/run_ref /tmp/run_new

`run_pipeline.sh` runs `dtfind`, `dtindex`, `dtrefine`, `dtintegrate` and
`dtscaleaverage` with stdin from `/dev/null`, so that prompts take their
defaults. `compare_runs.sh` requires reflection files to be identical byte
for byte, and headers and logs to be identical apart from time stamps, the
build date and the echoed command line. Run-to-run, the same build compares
identical.

For the default sweep the pipeline indexes the simulated cell (79.1, 79.1,
37.9 Å, P4 before `dtcell`), refines to an rms residual of 0.016 mm and
merges with Rmerge 0.075. The sweep is a fixture for detecting changes in
behaviour, not a test of data quality: the simulation is simple (flat
background, Gaussian spots, no detector gaps), and real data must also be
checked.

The reference build is the commit before the change under test, or for
compiler and flag changes, the legacy Makefile build.
