//
// Copyright (c) 2026 Graeme Winter
//
// Distributed under the same BSD 3-clause licence as the rest of d*TREK;
// see LICENSE at the top of the source tree.
//
// CXprop.cpp  -- no-X11 replacement for DTDISPLAY/CXprop.cc; see CXprop.h.
//

#include "CXprop.h"

CXprop::CXprop(const Cstring&, const char*) {}

CXprop::~CXprop() {}

unsigned long CXprop::hSetProperty(const Cstring&, const Cstring&, bool)
{
  return 0;
}
