/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file Closeness_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalCloseness.h"
#include "../python_binding.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalCloseness(pybind11::module_ &m) {
    m.def("temporal_closeness",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval, Distance_Type>(&temporal_closeness<TemporalEdge>),
          "Computes the temporal closeness centrality for a given source node within a specified time interval.\n\n"
          ":param tgs: The temporal graph.\n"
          ":param source_node: The source node ID.\n"
          ":param time_interval: The time interval (min_time, max_time) for which to compute closeness.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: The temporal closeness centrality of the source node.");

    m.def("temporal_closeness",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, Distance_Type>(&temporal_closeness<TemporalEdge>),
          "Computes the temporal closeness centrality for a given source node over the entire graph time interval.\n\n"
          ":param tgs: The temporal graph.\n"
          ":param source_node: The source node ID.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: The temporal closeness centrality of the source node.");

    m.def("temporal_closeness",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, TimeInterval, Distance_Type>(&temporal_closeness<TemporalEdge>),
          "Computes the temporal closeness centrality for all nodes within a specified time interval.\n\n"
          ":param tgs: The temporal graph.\n"
          ":param time_interval: The time interval (min_time, max_time) for which to compute closeness.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: A map of node IDs to their temporal closeness centrality.");

    m.def("temporal_closeness",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, Distance_Type>(&temporal_closeness<TemporalEdge>),
          "Computes the temporal closeness centrality for all nodes over the entire graph time interval.\n\n"
          ":param tgs: The temporal graph.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: A map of node IDs to their temporal closeness centrality.");

    m.def("run_temporal_closeness",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, Distance_Type>(&run_temporal_closeness<OrderedEdgeList<TemporalEdge>>),
          "Runs the temporal closeness centrality computation for all nodes.\n\n"
          ":param tgs: The temporal graph.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: A map of node IDs to their temporal closeness centrality.");

}

}