# CMake build for the d*TREK core library and command-line programs.
#
# The Motif GUIs (DTDISPLAY, DTPROCESS, DTCOLLECT, DTDEV) are not built.
#
#   cmake -S . -B build -G Ninja
#   cmake --build build
#
# Requires CBFlib (and the HDF5 headers, if CBFlib was built with HDF5).

cmake_minimum_required(VERSION 3.16)
project(dtrek VERSION 9.9.9.10 LANGUAGES C CXX)

option(DTREK_WITH_PTYPES
       "Build the socket interface to a controlling GUI (needs ptypes)" OFF)
option(DTREK_WITH_X11
       "Let command-line programs notify a running dtdisplay via X11" OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Build type" FORCE)
endif()

# The legacy Makefiles compile with -O1 -g, noting that dtsvd.cpp is
# miscompiled at -O2.  Keep that until the cause is understood.
set(CMAKE_C_FLAGS_RELWITHDEBINFO "-O1 -g")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O1 -g")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# --- Dependencies -----------------------------------------------------------

find_path(CBF_INCLUDE_DIR cbf.h PATH_SUFFIXES cbflib cbf)
find_library(CBF_LIBRARY NAMES cbf)
if(NOT CBF_INCLUDE_DIR OR NOT CBF_LIBRARY)
  message(FATAL_ERROR "CBFlib not found: set CBF_INCLUDE_DIR and CBF_LIBRARY")
endif()

# Recent CBFlib headers include hdf5.h.
find_package(HDF5 COMPONENTS C)

find_package(Threads REQUIRED)

# --- Core library -----------------------------------------------------------

add_library(dtrek STATIC
    DTTREK/BitmapRLE.cpp
    DTTREK/C3Ddata.cpp
    DTTREK/CBackground.cpp
    DTTREK/CBeamData.cpp
    DTTREK/CCellReduce.cpp
    DTTREK/CCommandLine.cpp
    DTTREK/CExperimentalStrategy.cpp
    DTTREK/CEyeballIndex.cpp
    DTTREK/CGonioMask.cpp
    DTTREK/CGonioShadow.cpp
    DTTREK/CIceRingLocator.cpp
    DTTREK/CImageWait.cpp
    DTTREK/CScanBitmap.cpp
    DTTREK/CSphericalHarmonic.cpp
    DTTREK/Cabsence.cpp
    DTTREK/Ccompare.cpp
    DTTREK/Ccrystal.cpp
    DTTREK/Cdetector.cpp
    DTTREK/Cfind.cpp
    DTTREK/Cgoniometer.cpp
    DTTREK/Cimage.cpp
    DTTREK/Cimage_header.cpp
    DTTREK/Cindex.cpp
    DTTREK/Cintegrate.cpp
    DTTREK/CinterpMesh.cpp
    DTTREK/Claue.cpp
    DTTREK/Cnonunf.cpp
    DTTREK/Corient.cpp
    DTTREK/Cpredict.cpp
    DTTREK/Cprofit2D.cpp
    DTTREK/Crefine.cpp
    DTTREK/Crefln.cpp
    DTTREK/Creflnlist.cpp
    DTTREK/Crotation.cpp
    DTTREK/Cscale.cpp
    DTTREK/Cscaleaverage.cpp
    DTTREK/Cscan.cpp
    DTTREK/Csource.cpp
    DTTREK/Cspacegroup.cpp
    DTTREK/Cspacegroup_check.cpp
    DTTREK/Cspatial.cpp
    DTTREK/Cstat.cpp
    DTTREK/Cstrategy.cpp
    DTTREK/Cstring.cpp
    DTTREK/Cwavelength.cpp
    DTTREK/DTCoreSocket.cpp
    DTTREK/DTCoreTclParam.cpp
    DTTREK/DTMain.cpp
    DTTREK/DTMainAverage.cpp
    DTTREK/DTMainBeamMask.cpp
    DTTREK/DTMainCell.cpp
    DTTREK/DTMainCompare.cpp
    DTTREK/DTMainExtractHeader.cpp
    DTTREK/DTMainFind.cpp
    DTTREK/DTMainHeaderEdit.cpp
    DTTREK/DTMainIndex.cpp
    DTTREK/DTMainIntegrate.cpp
    DTTREK/DTMainMultiStrategy.cpp
    DTTREK/DTMainPredict.cpp
    DTTREK/DTMainProfit.cpp
    DTTREK/DTMainRank.cpp
    DTTREK/DTMainRanker.cpp
    DTTREK/DTMainRefine.cpp
    DTTREK/DTMainReflnMerge.cpp
    DTTREK/DTMainScaleAverage.cpp
    DTTREK/DTMainStrategy.cpp
    DTTREK/ImagePool.cpp
    DTTREK/NTHUfixup.cpp
    DTTREK/ResoBins.cpp
    DTTREK/StrategyScans.cpp
    DTTREK/adscccd.cpp
    DTTREK/brandeisccd.cpp
    DTTREK/bs.cpp
    DTTREK/cbfdtrek.cpp
    DTTREK/dip2030.cpp
    DTTREK/dskio.cpp
    DTTREK/dtarray.cpp
    DTTREK/dtreklogic.cpp
    DTTREK/dtreksys.cpp
    DTTREK/dtrekvec.cpp
    DTTREK/dtsvd.cpp
    DTTREK/hipic.cpp
    DTTREK/marccd.cpp
    DTTREK/marip.cpp
    DTTREK/medoptics.cpp
    DTTREK/pck.c
    DTTREK/raxis.cpp
    DTTREK/winbmp.cpp)

target_include_directories(dtrek PUBLIC DTTREK ${CBF_INCLUDE_DIR})
target_compile_definitions(dtrek PUBLIC NEW_IOS BINARY_NOT_BIN NO_MFC)
if(APPLE)
  target_compile_definitions(dtrek PUBLIC OSX)
elseif(UNIX)
  target_compile_definitions(dtrek PUBLIC LINUX _GNU_SOURCE)
endif()
target_link_libraries(dtrek PUBLIC ${CBF_LIBRARY} Threads::Threads
                      ${CMAKE_DL_LIBS})
if(HDF5_FOUND)
  target_include_directories(dtrek PUBLIC ${HDF5_INCLUDE_DIRS})
  target_link_libraries(dtrek PUBLIC ${HDF5_C_LIBRARIES})
endif()
if(NOT APPLE AND NOT WIN32)
  target_link_libraries(dtrek PUBLIC m)
endif()

# Legacy compilation settings: the code predates standard C++ in places.
target_compile_options(dtrek PUBLIC
  -w)

if(DTREK_WITH_PTYPES)
  find_path(PTYPES_INCLUDE_DIR pinet.h PATH_SUFFIXES ptypes)
  find_library(PTYPES_LIBRARY NAMES ptypes)
  if(NOT PTYPES_INCLUDE_DIR OR NOT PTYPES_LIBRARY)
    message(FATAL_ERROR "DTREK_WITH_PTYPES is ON but ptypes was not found")
  endif()
  target_compile_definitions(dtrek PUBLIC DTREK_HAVE_PTYPES)
  target_include_directories(dtrek PUBLIC ${PTYPES_INCLUDE_DIR})
  target_link_libraries(dtrek PUBLIC ${PTYPES_LIBRARY})
endif()

if(DTREK_WITH_X11)
  find_package(X11 REQUIRED)
  target_sources(dtrek PRIVATE DTDISPLAY/CXprop.cc)
  set_source_files_properties(DTDISPLAY/CXprop.cc PROPERTIES LANGUAGE CXX)
  target_include_directories(dtrek PUBLIC DTDISPLAY ${X11_INCLUDE_DIR})
  target_link_libraries(dtrek PUBLIC ${X11_LIBRARIES})
else()
  target_sources(dtrek PRIVATE DTTREK/nox11/CXprop.cpp)
  target_include_directories(dtrek PUBLIC DTTREK/nox11)
endif()

# --- Programs ---------------------------------------------------------------

set(DTREK_PROGRAMS
    dtfind
    dtpixhist
    dtindex
    dtrefine
    dtpredict
    dtstrategy
    dtmultistrategy
    dtintegrate
    dtprofit
    dtreflnmerge
    dtbeammask
    dtscaleaverage
    dtorient
    dtheaderedit
    dtrank
    dtranker
    dtnonunfedit
    dtaverage
    dtrek2raxis
    dtextractheader
    dtdezinger
    dtdarksubtract
    dtraxis
    dtcreate
    dtadd2
    dtcompare
    dtcompose
    dtdecompose
    dtbin
    dtheadermerge
    dtcell
    dtsmooth
    dtx2refln
    dtsbcdark
    dtsbcdarkmask
    dtrebatch
    sca2dtrek
    dtscale2sca)

foreach(program IN LISTS DTREK_PROGRAMS)
  add_executable(${program} DTTREK/${program}.cpp)
  target_link_libraries(${program} PRIVATE dtrek)
  set_target_properties(${program} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endforeach()

# dtdisplayupdate exists only to send properties to dtdisplay.
if(DTREK_WITH_X11)
  add_executable(dtdisplayupdate DTTREK/dtdisplayupdate.cpp)
  target_link_libraries(dtdisplayupdate PRIVATE dtrek)
  set_target_properties(dtdisplayupdate PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
  list(APPEND DTREK_PROGRAMS dtdisplayupdate)
endif()

include(GNUInstallDirs)
install(TARGETS ${DTREK_PROGRAMS} RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
