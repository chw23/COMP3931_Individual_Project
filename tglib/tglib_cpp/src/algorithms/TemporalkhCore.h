/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/** @file TemporalkhCore.h
 *  @brief Contains function for computing the temporal (k,h)-cores.
 */
#ifndef TGLIB_TEMPORALKHCORE_H
#define TGLIB_TEMPORALKHCORE_H

#include <vector>
#include <map>
#include <set>
#include "../core/AggregatedGraph.h"
#include "../core/OrderedEdgeList.h"
#include "../core/Transformations.h"
#include "StatickCore.h"

namespace tglib {

/**
 * The computes the (k,h)-core numbers as defined in:
 *
 * Wu, Huanhuan, et al. "Core decomposition in large temporal graphs." 2015 IEEE International Conference on Big Data (Big Data). IEEE, 2015.
 *
 * @tparam E Temporal edge type
 * @param tgs Ordered edge list
 * @param h Paramter h
 * @return The (k,h)-core numbers.
 */
template<typename E>
std::vector<NodeId> compute_khcores(OrderedEdgeList<E> const &tgs, uint h) {
    auto g = to_aggregated_edge_list<E>(tgs);
    std::vector<StaticWeightedEdge> edges;
    for (auto &e : g) {
        if (e.weight >= h) {
            edges.push_back(e);
        }
    }
    return compute_kcores<StaticWeightedEdge>(edges);
}

}

#endif //TGLIB_TEMPORALKHCORE_H
