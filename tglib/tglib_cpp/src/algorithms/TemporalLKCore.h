/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/** @file TemporalLKCore.h
 *  @brief Contains function for computing the temporal (L,K)-cores.
 */

#ifndef TGLIB_TEMPORALLKLASTINGCORE_H
#define TGLIB_TEMPORALLKLASTINGCORE_H


#include <vector>
#include <map>
#include <set>
#include <list>
#include "../core/AggregatedGraph.h"
#include "../core/OrderedEdgeList.h"
#include "../core/Transformations.h"
#include "StatickCore.h"


namespace tglib {

/**
 * The computes the maximal (L,K)-core as defined in:
 *
 * Wei-Chun Hung and Chih-Ying Tseng. 2021. Maximum (L, K)-Lasting Cores in Temporal Social Networks. In DASFAA Intl Workshops. Cham, 336–352.
 *
 * @tparam E Temporal edge type
 * @param tgs Ordered edge list
 * @param h Paramter L
 * @param h Paramter k
 * @return The maximal (L,K)-lasting core.
 */
template<typename E>
std::vector<NodeId> compute_LKcores(OrderedEdgeList<E> const &tgs, uint L, uint k) {
    std::list<E> current_edges;
    std::set<Time> timestamps;

    for (auto &e : tgs.getEdges()) {
        timestamps.insert(e.t);
    }

    std::vector<Time> times = {timestamps.begin(), timestamps.end()};
    std::vector<NodeId> result;
    std::vector<NodeId> final_r;
    std::set<uint> final_num_cores;

    std::pair<Time, Time> interval;

    auto edges_it = tgs.getEdges().begin();
    for (size_t i = 0; i < times.size()-L; ++i) {
        while (!current_edges.empty() && current_edges.front().t < times[i]) current_edges.pop_front();
        while (current_edges.empty() || (*edges_it).t < times[i + L]) {
            current_edges.push_back(*edges_it++);
        }

        std::map<std::pair<NodeId, NodeId>, uint> em;
        for (auto &e: current_edges) em[{e.u, e.v}] += 1;

        std::vector<StaticWeightedEdge> intersection;
        for (auto &[p, v]: em) {
            if (v == L) intersection.push_back({p.first, p.second, 1});
        }

        auto r = compute_kcores<StaticWeightedEdge>(intersection);
        std::vector<NodeId> tmp;
        std::set<uint> num_cores;
        for (size_t j = 0; j < r.size(); ++j) {
            if ((uint)r[j] >= k) {
                tmp.push_back((NodeId)j);
                num_cores.insert(r[j]);
            }
        }
        if (tmp.size() > result.size()) {
            interval = {times[i], times[i+L]};
            result = tmp;
            final_num_cores = num_cores;
            final_r = r;
        }

    }

    return result;
}

}


#endif //TGLIB_TEMPORALLKLASTINGCORE_H
