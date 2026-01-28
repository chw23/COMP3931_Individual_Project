/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file AggregatedGraph_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../core/AggregatedGraph.h"

namespace tglib_python_binding {

using namespace tglib;

void bind_AggregatedGraph(pybind11::module_ &m) {

    pybind11::class_<StaticWeightedEdge>(m, "StaticWeightedEdge", "Represents a static weighted edge.")
            .def(pybind11::init<>(), "Default constructor.")
            .def_readwrite("u", &StaticWeightedEdge::u, "The source node ID.")
            .def_readwrite("v", &StaticWeightedEdge::v, "The target node ID.")
            .def_readwrite("weight", &StaticWeightedEdge::weight, "The weight of the edge.")
            ;

}

} // tglib_python_binding