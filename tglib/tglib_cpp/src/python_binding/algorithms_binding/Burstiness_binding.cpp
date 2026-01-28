/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file Burstiness_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/Burstiness.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_Burstiness(pybind11::module_ &m) {
    m.def("edge_burstiness",&edge_burstiness<TemporalEdge>,
    "Computes the edge burstiness for all (static) edges.\n\n"
    "Burstiness measures how much a sequence of contacts of a pair of edges deviates from the\n"
    "memoryless random Poisson process.\n\n"
    ":param tgs: The temporal graph as ordered edge list.\n"
    ":param ti: The time interval for which the edge_burstiness is computed.\n"
    ":return: For each pair of nodes with at least one temporal edge connecting them, the edge_burstiness of the tie.");

    m.def("node_burstiness", &node_burstiness<TemporalEdge>,
    "Computes the edge burstiness for all nodes.\n\n"
    "Burstiness measures how much a sequence of contacts of a single node deviates from the\n"
    "memoryless random Poisson process.\n\n"
    ":param tgs: The temporal graph as ordered edge list.\n"
    ":param ti: The time interval for which the node burstiness is computed.\n"
    ":return: For each node the node burstiness.");
}

}