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
#include "../../algorithms/TemporalEfficiency.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_TemporalEfficiency(pybind11::module_ &m) {

    m.def("temporal_efficiency",
          pybind11::overload_cast<OrderedEdgeList<TemporalEdge> const&, TimeInterval, Distance_Type>(
                  &temporal_efficiency<OrderedEdgeList<TemporalEdge>>),
          "Computes the temporal efficiency of the graph.\n\n"
          ":param tg: The temporal graph as an ordered edge list.\n"
          ":param time_interval: The time interval for which to compute the efficiency.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: The temporal efficiency of the graph.");

    m.def("temporal_efficiency",
          pybind11::overload_cast<IncidentLists<TGNode, TemporalEdge> const&, TimeInterval, Distance_Type>(
                  &temporal_efficiency<IncidentLists<TGNode, TemporalEdge>>),
          "Computes the temporal efficiency of the graph.\n\n"
          ":param tg: The temporal graph as incident lists.\n"
          ":param time_interval: The time interval for which to compute the efficiency.\n"
          ":param distance_type: The type of distance to use (e.g., Fastest, Earliest_Arrival).\n"
          ":return: The temporal efficiency of the graph.");

}

}