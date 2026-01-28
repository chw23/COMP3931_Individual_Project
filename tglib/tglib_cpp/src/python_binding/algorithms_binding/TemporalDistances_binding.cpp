/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file Distances_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalDistances.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalDistances(pybind11::module_ &m) {
    m.def("minimum_durations",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval>(&minimum_durations<TemporalEdge>),
          R"doc(Computes the durations of fastest paths from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tgs: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The durations of the fastest paths.)doc");

    m.def("minimum_durations",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval>(&minimum_durations<TGNode, TemporalEdge>),
          R"doc(Computes the durations of fastest paths from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tg: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The durations of the fastest paths.)doc");


    m.def("earliest_arrival_times",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval>(&earliest_arrival_times<TemporalEdge>),
          R"doc(Computes the earliest arrival times from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tgs: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The earliest arrival times.)doc");

    m.def("earliest_arrival_times",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval>(&earliest_arrival_times<TGNode, TemporalEdge>),
          R"doc(Computes the earliest arrival times from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tg: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The earliest arrival times.)doc");


    m.def("latest_departure_times",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval>(&latest_departure_times<TemporalEdge>),
          R"doc(Computes the latest departure times from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tgs: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The lastest departure times.)doc");


    m.def("minimum_hops",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval>(&minimum_hops<TemporalEdge>),
          R"doc(Computes the minimum number of hops from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tgs: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The minimum number of hops.)doc");

    m.def("minimum_hops",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval>(&minimum_hops<TGNode, TemporalEdge>),
          R"doc(Computes the minimum number of hops from the node with id nid to all other, during the time interval ti reachable, nodes.

:param tg: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The minimum number of hops.)doc");


    m.def("minimum_transition_times",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval>(&minimum_transition_times<TemporalEdge>),
          R"doc(Computes the minimum sum of transition times from the node with id nid to all, other during the time interval ti reachable, nodes.

:param tgs: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The minimum sum of transition times.)doc");

    m.def("minimum_transition_times",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval>(&minimum_transition_times<TGNode, TemporalEdge>),
          R"doc(Computes the minimum sum of transition times from the node with id nid to all, other during the time interval ti reachable, nodes.

:param tg: The temporal graph.
:param nid: The query node id.
:param ti: The restrictive time interval.
:return: The minimum sum of transition times.)doc");

}

}