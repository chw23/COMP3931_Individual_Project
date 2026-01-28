/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file IncidentLists_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../core/Transformations.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_Transformations(pybind11::module_ &m) {
    m.def("to_incident_lists", &to_incident_lists<TGNode, TemporalEdge>, "Converts an OrderedEdgeList to an IncidentLists representation.");
    m.def("to_trs_graph", &to_trs_graph<TemporalEdge>, "Converts an OrderedEdgeList to a TRSGraph representation.");
    m.def("to_directed_line_graph",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&>(&to_directed_line_graph<TemporalEdge>), "Converts an OrderedEdgeList to a directed line graph.");
    m.def("to_aggregated_edge_list", &to_aggregated_edge_list<TemporalEdge>, "Aggregates temporal edges into a static weighted edge list.");
    m.def("normalize", normalize<TemporalEdge>, "Normalizes the timestamps of temporal edges to start from 0.");
    m.def("scale_timestamps", scale_timestamps<TemporalEdge>, "Scales the timestamps of temporal edges to a new range.");
    m.def("unit_transition_times", unit_transition_times<TemporalEdge>, "Sets all transition times of temporal edges to 1.");
    m.def("make_undirected", make_undirected<TemporalEdge>, "Converts a directed temporal graph to an undirected one by adding reverse edges.");
}

} // tglib_python_binding