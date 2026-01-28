/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/**
 * @file InputOutput_binding.cpp
 * @brief This file provides the python binding code.
 *
 */

#include <pybind11/pybind11.h>
#include "../../util/InputOutput.h"

namespace tglib_python_binding {

using namespace tglib;
using namespace tglib;

void bind_InputOutput(pybind11::module_ &m) {
    m.def("load_ordered_edge_list",
          pybind11::overload_cast<std::string const&>(&load_ordered_edge_list<TemporalEdge>),
          "Loads a temporal graph from a file into an OrderedEdgeList representation.\n\n"
          ":param file_path: The path to the input file.\n"
          ":return: An OrderedEdgeList containing the temporal graph data.");
    m.def("load_ordered_edge_list",
          pybind11::overload_cast<std::string const&, bool>(&load_ordered_edge_list<TemporalEdge>),
          "Loads a temporal graph from a file into an OrderedEdgeList representation, with an option to ignore self-loops.\n\n"
          ":param file_path: The path to the input file.\n"
          ":param ignore_self_loops: If true, self-loops (edges from a node to itself) are ignored.\n"
          ":return: An OrderedEdgeList containing the temporal graph data.");
}

} // tglib_python_binding