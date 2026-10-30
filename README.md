# d*TREK

d*TREK is a suite of C++ classes and programs that is used to process X-ray diffraction data from area detectors. It supports processing of data from multiple detector types (imaging plates, CCDs and pixel arrays) and from multiple vendors (Rigaku, Mar, Dectris, Bruker and ADSC to name a few).

Development of d\*TREK begin in 1994 with a DOE grant (written by Jim Pflugrath and Ed Westbrook) to support the APS-1 CCD detector at the APS. In the years since, development of d\*TREK has been funded by Rigaku.

Please note that d\*TREK is not thread safe.

Also, note that because of licensing issues, the open source version of d\*TREK contains neither the Reqab absorption correction nor the absorption correction written by Higashi. It also does not make any use of collision file information during the strategy generation. Finally, this version does not require a license for operation.

## Building

The core library and command-line programs (`dtfind`, `dtindex`,
`dtrefine`, `dtintegrate`, `dtscaleaverage`, ...) are built with CMake. The
Motif GUIs in `DTDISPLAY`, `DTPROCESS`, `DTCOLLECT` and `DTDEV` are not built.

    cmake -S . -B build -G Ninja
    cmake --build build

The programs are placed in `build/bin`. The only required dependency is
[CBFlib](https://github.com/yayahjb/cbflib) (for example `libcbf-dev` on
Debian and Ubuntu, or `cbflib` from conda-forge); if CBFlib was built with
HDF5, the HDF5 headers are needed too.

Options:

| Option | Default | Effect |
|---|---|---|
| `DTREK_WITH_PTYPES` | `OFF` | Build the socket interface to a controlling GUI, which needs the [ptypes](http://www.melikyan.com/ptypes/) library. Without it, socket connections fail cleanly. |
| `DTREK_WITH_X11` | `OFF` | Let the programs notify a running `dtdisplay` through X11 window properties, and build `dtdisplayupdate`. |

The legacy Makefiles are kept for reference.

