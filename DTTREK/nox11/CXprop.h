//
// Copyright (c) 2026 Graeme Winter
//
// Distributed under the same BSD 3-clause licence as the rest of d*TREK;
// see LICENSE at the top of the source tree.
//
// CXprop.h  -- no-X11 replacement for DTDISPLAY/CXprop.h
//
// The command-line programs use CXprop only to tell a running dtdisplay
// (via an X11 window property) to show new results.  When d*TREK is built
// without X11 (the default, and the only option where X11 is unavailable)
// this class is used instead: it has the same interface as far as the
// command-line programs use it, and does nothing.
//

#ifndef DT_CXPROP_H
#define DT_CXPROP_H

#include "Cstring.h"

class CXprop {
public:
  CXprop(const Cstring& sWindowName, const char* pcDisplayName = NULL);
  ~CXprop();

  // Always returns 0 (None): there is no display to notify.
  unsigned long hSetProperty(const Cstring& sPropertyName,
                             const Cstring& sPropText, bool bIfOnly = true);
};

#endif  // DT_CXPROP_H
