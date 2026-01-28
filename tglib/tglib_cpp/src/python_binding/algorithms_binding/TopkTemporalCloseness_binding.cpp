/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TopkTemporalCloseness_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TopkTemporalCloseness.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TopkTemporalCloseness(pybind11::module_ &m) {
    m.def("compute_topk_closeness",&compute_topk_closeness<TGNode, TemporalEdge>,
          "Computes the top-k temporal closeness centrality for nodes.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param k: The number of top nodes to return.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: A list of pairs, where each pair contains a node ID and its temporal closeness centrality, sorted by closeness in descending order.");
}

}