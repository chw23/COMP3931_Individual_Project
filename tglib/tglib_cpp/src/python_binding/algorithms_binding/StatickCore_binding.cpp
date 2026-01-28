/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file StatickCore_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalkhCore.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_StatickCores(pybind11::module_ & m) {
    m.def("kcores", &compute_kcores<StaticWeightedEdge>,
    "Computes the k-core values for all nodes.\n\n"
    ":param edges: The aggregated graph as edge list.\n"
    ":return: Vector of core numbers.");
}

} // tglib_python_binding