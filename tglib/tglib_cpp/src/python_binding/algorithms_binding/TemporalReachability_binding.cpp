/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalReachability.h"

namespace tglib_python_binding {

using namespace tglib;


/**
 * @file TemporalReachability_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

void bind_TemporalReachability(pybind11::module_ &m) {
    m.def("number_of_reachable_nodes",
          pybind11::overload_cast < OrderedEdgeList < TemporalEdge > const&, NodeId, TimeInterval >
                                                                                     (&number_of_reachable_nodes <
                                                                                      TemporalEdge > ),
          "Computes the number of reachable nodes from a given source node within a specified time interval.\n\n"
          ":param tgs: The temporal graph as an ordered edge list.\n"
          ":param source_node: The source node ID.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":return: The number of reachable nodes.");

}

}