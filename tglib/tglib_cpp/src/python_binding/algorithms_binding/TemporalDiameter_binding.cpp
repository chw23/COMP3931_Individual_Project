/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file TemporalEfficiency_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../algorithms/TemporalDiameter.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalDiameter(pybind11::module_ &m) {

    m.def("temporal_diameter",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, TimeInterval, Distance_Type>(
            &temporal_diameter<OrderedEdgeList<TemporalEdge>>),
            "Computes the temporal diameter, e.g., max. eccentricity in the temporal graph.\n\n"
            ":param tg: The temporal graph.\n"
            ":param timeInterval: The restrictive time interval.\n"
            ":param distanceType: The distance type.\n"
            ":return: The temporal diameter of tg.");

    m.def("temporal_diameter",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, TimeInterval, Distance_Type>(
            &temporal_diameter<IncidentLists<TGNode, TemporalEdge>>),
            "Computes the temporal diameter, e.g., max. eccentricity in the temporal graph.\n\n"
            ":param tg: The temporal graph.\n"
            ":param timeInterval: The restrictive time interval.\n"
            ":param distanceType: The distance type.\n"
            ":return: The temporal diameter of tg.");


    m.def("temporal_eccentricity",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, NodeId, TimeInterval, Distance_Type>(
            &temporal_eccentricity<OrderedEdgeList<TemporalEdge>>),
            "Computes the maximum optimal temporal distance to any reachable vertex.\n\n"
            ":param tg: The temporal graph.\n"
            ":param nid: The node id.\n"
            ":param timeInterval: The restrictive time interval.\n"
            ":param distanceType: The distance type.\n"
            ":return: The eccentricity of node nid.");

    m.def("temporal_eccentricity",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, NodeId, TimeInterval, Distance_Type>(
            &temporal_eccentricity<IncidentLists<TGNode, TemporalEdge>>),
            "Computes the maximum optimal temporal distance to any reachable vertex.\n\n"
            ":param tg: The temporal graph.\n"
            ":param nid: The node id.\n"
            ":param timeInterval: The restrictive time interval.\n"
            ":param distanceType: The distance type.\n"
            ":return: The eccentricity of node nid.");

}

}