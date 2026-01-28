/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TemporalClusteringCoefficient_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalClusteringCoefficient.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalClusteringCoefficient(pybind11::module_ &m) {

    m.def("temporal_clustering_coefficient",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, TimeInterval>(&temporal_clustering_coefficient<TGNode, TemporalEdge>),
          "Computes the temporal clustering coefficient for all nodes within a specified time interval.\n\n"
          ":param tgs: The temporal graph as incident lists.\n"
          ":param time_interval: The time interval (min_time, max_time) for which to compute the clustering coefficient.\n"
          ":return: A map of node IDs to their temporal clustering coefficient.");

    m.def("temporal_clustering_coefficient",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval>(&temporal_clustering_coefficient<TGNode, TemporalEdge>),
          "Computes the temporal clustering coefficient for a given node within a specified time interval.\n\n"
          ":param tgs: The temporal graph as incident lists.\n"
          ":param node_id: The ID of the node for which to compute the clustering coefficient.\n"
          ":param time_interval: The time interval (min_time, max_time) for which to compute the clustering coefficient.\n"
          ":return: The temporal clustering coefficient of the specified node.");

}

}