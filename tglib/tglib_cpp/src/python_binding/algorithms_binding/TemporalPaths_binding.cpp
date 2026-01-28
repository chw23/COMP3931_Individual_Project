/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TemporalPaths_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalPaths.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalPaths(pybind11::module_ &m) {
    m.def("minimum_duration_path", &minimum_duration_path<TGNode, TemporalEdge>,
          "Computes the minimum duration path between two nodes.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param source_node: The source node ID.\n"
          ":param target_node: The target node ID.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":return: The minimum duration path as a list of temporal edges.");
    m.def("earliest_arrival_path", &earliest_arrival_path<TGNode, TemporalEdge>,
          "Computes the earliest arrival path between two nodes.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param source_node: The source node ID.\n"
          ":param target_node: The target node ID.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":return: The earliest arrival path as a list of temporal edges.");
    m.def("minimum_transition_time_path", &minimum_transition_time_path<TGNode, TemporalEdge>,
          "Computes the path with the minimum number of transitions between two nodes.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param source_node: The source node ID.\n"
          ":param target_node: The target node ID.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":return: The minimum transition time path as a list of temporal edges.");
    m.def("minimum_hops_path", &minimum_hops_path<TGNode, TemporalEdge>,
          "Computes the path with the minimum number of hops between two nodes.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param source_node: The source node ID.\n"
          ":param target_node: The target node ID.\n"
          ":param time_interval: The restrictive time interval.\n"
          ":return: The minimum hops path as a list of temporal edges.");
}

}