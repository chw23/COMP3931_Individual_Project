/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TemporalLKCore_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalLKCore.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalLKCores(pybind11::module_ & m) {
    m.def("temporal_LKcores", &compute_LKcores<TemporalEdge>,
          "Computes the temporal (L,k)-cores for all nodes.\n\n"
          ":param tgs: The temporal graph as an ordered edge list.\n"
          ":return: A map of node IDs to their (L,k)-core values.");
}

} // tglib_python_binding