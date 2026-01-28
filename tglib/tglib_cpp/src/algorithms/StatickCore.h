/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */


#include <cstdlib>
#include <vector>
#include <map>
#include <set>
#include "../core/AggregatedGraph.h"

#ifndef TGLIB_STATICKCORE_H
#define TGLIB_STATICKCORE_H


namespace tglib {

/**
 * Computes the k-core values for all nodes.
 * @param edges The aggregated graph as edge list.
 * @return Vector of core numbers.
 */
 template<class E>
std::vector<NodeId> compute_kcores(std::vector<E> const &edges) {
    std::map<uint, std::vector<E>> g;

    NodeId mxnid = 0;
    for (auto &e : edges) {
        g[e.u].push_back(e); // todo assumption graph is undirected
        g[e.v].push_back(e); // todo assumption graph is undirected
        if (e.u > mxnid) mxnid = e.u;
        if (e.v > mxnid) mxnid = e.v;
    }

    std::set<std::pair<uint, NodeId>, std::less<>> degrees;
    std::vector<NodeId> c(mxnid+1, 0);
    for (auto &p : g) {
        degrees.insert({p.second.size(), p.first});
        c[p.first] = p.second.size();
    }

    std::vector<bool> removed(mxnid+1, false);

    while (!degrees.empty() ) {
        auto next = degrees.begin();
        auto u = next->second;
        degrees.erase(next);

        if (removed[u]) continue;
        removed[u] = true;

        for (auto &e : g[u]) {
            if (removed[e.v]) continue;
            if (c[e.v] > c[e.u]) {
                --c[e.v];
                degrees.insert({c[e.v], e.v});
            }
        }
    }

    return c;
}

}

#endif //TGLIB_STATICKCORE_H
