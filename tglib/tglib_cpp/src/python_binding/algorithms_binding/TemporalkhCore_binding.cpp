/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TemporalkhCore_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalkhCore.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalkhCores(pybind11::module_ & m) {
    m.def("temporal_khcores", &compute_khcores<TemporalEdge>,
          "Computes the temporal (k,h)-cores for all nodes.\n\n"
          ":param tgs: The temporal graph as an ordered edge list.\n"
          ":return: A map of node IDs to their (k,h)-core values.");
}

} // tglib_python_binding