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
#include "../../core/IncidentLists.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_IncidentLists(pybind11::module_ &m) {

    pybind11::class_<TGNode>(m, "TGNode")
            .def(pybind11::init<>())
            .def_readwrite("id", &TGNode::id)
            .def_readwrite("outEdges", &TGNode::outEdges)
            ;

    pybind11::class_<IncidentLists<TGNode, TemporalEdge>>(m, "IncidentLists", "Represents a temporal graph using incident lists.")
            .def(pybind11::init<>(), "Default constructor.")
            .def(pybind11::init<NodeId, const std::vector<TemporalEdge> &>(), "Constructor with number of nodes and temporal edges.")
            .def("getNode", &IncidentLists<TGNode, TemporalEdge>::getNode, "Returns a node by its ID.")
            .def("getNodes", &IncidentLists<TGNode, TemporalEdge>::getNodes, "Returns a map of all nodes in the graph.")
            .def("getNumberOfNodes", &IncidentLists<TGNode, TemporalEdge>::getNumberOfNodes, "Returns the number of nodes in the graph.")
            .def("getNumberOfEdges", &IncidentLists<TGNode, TemporalEdge>::getNumberOfEdges, "Returns the number of temporal edges in the graph.")
            .def("getTimeInterval", &IncidentLists<TGNode, TemporalEdge>::getTimeInterval, "Returns the time interval of the graph (min_timestamp, max_timestamp).")
            ;
}

} // tglib_python_binding