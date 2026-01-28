/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file BasicTypes_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>

#include "../../core/BasicTypes.h"
#include "../../core/AggregatedGraph.h"
#include <map>

namespace tglib_python_binding {

using namespace tglib;

void bind_BasicTypes(pybind11::module_ &m) {
    pybind11::bind_vector<std::vector<double>>(m, "VectorDouble");
    pybind11::bind_vector<std::vector<Time>>(m, "VectorTime");
    pybind11::bind_vector<std::vector<NodeId>>(m, "VectorNodeId");
    pybind11::bind_vector<std::vector<uint>>(m, "VectorUnsignedInt");
    pybind11::bind_vector<std::vector<TemporalEdge>>(m, "VectorTemporalEdge");
    pybind11::bind_vector<std::vector<StaticWeightedEdge>>(m, "VectorStaticWeightedEdge");
    pybind11::bind_map<std::map<std::pair<NodeId, NodeId>, double>>(m, "MapPairNodeIdsDouble");
    pybind11::bind_vector<std::vector<std::pair<tglib::NodeId, double>>>(m, "VectorNodeIdDoublePair");

    pybind11::enum_<Distance_Type>(m, "Distance_Type", "An enum type for distance types.")
            .value("Fastest", Distance_Type::Fastest, "Fastest path distance type.")
            .value("Earliest_Arrival", Distance_Type::Earliest_Arrival, "Earliest arrival path distance type.")
            .value("Minimum_Transition_Times", Distance_Type::Minimum_Transition_Times, "Minimum transition times path distance type.")
            .value("Minimum_Hops", Distance_Type::Minimum_Hops, "Minimum hops path distance type.")
            .value("Latest_Departure", Distance_Type::Latest_Departure, "Latest departure path distance type.")
            ;

    pybind11::class_<TemporalGraphStatistics>(m, "TemporalGraphStatistics", "A class to store temporal graph statistics.")
            .def(pybind11::init<>(), "Default constructor.")
            .def_readwrite("numberOfNodes", &TemporalGraphStatistics::numberOfNodes, "The number of nodes in the graph.")
            .def_readwrite("numberOfEdges", &TemporalGraphStatistics::numberOfEdges, "The number of temporal edges in the graph.")
            .def_readwrite("numberOfStaticEdges", &TemporalGraphStatistics::numberOfStaticEdges, "The number of static edges in the graph.")
            .def_readwrite("numberOfTimeStamps", &TemporalGraphStatistics::numberOfTimeStamps, "The number of unique timestamps in the graph.")
            .def_readwrite("numberOfTransitionTimes", &TemporalGraphStatistics::numberOfTransitionTimes, "The number of unique transition times in the graph.")
            .def_readwrite("minimalTimeStamp", &TemporalGraphStatistics::minimalTimeStamp, "The minimal timestamp in the graph.")
            .def_readwrite("maximalTimeStamp", &TemporalGraphStatistics::maximalTimeStamp, "The maximal timestamp in the graph.")
            .def_readwrite("minimalTransitionTime", &TemporalGraphStatistics::minimalTransitionTime, "The minimal transition time in the graph.")
            .def_readwrite("maximalTransitionTime", &TemporalGraphStatistics::maximalTransitionTime, "The maximal transition time in the graph.")
            .def_readwrite("maxTemporalInDegree", &TemporalGraphStatistics::maxTemporalInDegree, "The maximum temporal in-degree.")
            .def_readwrite("minTemporalInDegree", &TemporalGraphStatistics::minTemporalInDegree, "The minimum temporal in-degree.")
            .def_readwrite("maxTemporalOutDegree", &TemporalGraphStatistics::maxTemporalOutDegree, "The maximum temporal out-degree.")
            .def_readwrite("minTemporalOutDegree", &TemporalGraphStatistics::minTemporalOutDegree, "The minimum temporal out-degree.")
            .def("__str__", &TemporalGraphStatistics::toString, "Returns a string representation of the statistics.")
            ;
}

} // tglib_python_binding