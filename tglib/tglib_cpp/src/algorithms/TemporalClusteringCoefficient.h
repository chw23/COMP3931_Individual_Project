/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/** @file TemporalClusteringCoefficient.h
 *  @brief Contains function for computing the temporal clustering coefficient.
 */

#ifndef TGLIB_TEMPORALCLUSTERINGCOEFFICIENT_H
#define TGLIB_TEMPORALCLUSTERINGCOEFFICIENT_H

#include "../core/BasicTypes.h"
#include "../core/IncidentLists.h"

namespace tglib {

/**
 * @brief Computes the temporal clustering coefficient for one node
 *
 * The temporal clustering coefficient is defined as
 * \f[
 * C_C(u) = \frac{\sum_{t\in T(\mathcal{G})} \pi_t(u)}{|T(\mathcal{G})|{|N(u)| \choose 2}},
 * \f]
 * where \f$\pi_t(u)=|\{(v,w,t,\lambda)\in\mathcal{E}\mid v,w\in N(u)\}|\f$
 * and \f$N(u)\f$ the neighbors of \f$u\f$ [1].
 *
 * [1] Tang, John, et al. "Temporal distance metrics for social network analysis."
 * Proceedings of the 2nd ACM workshop on Online social networks. 2009.
 *
 * @tparam N Node type
 * @param tg The temporal graph
 * @param nid The node for which the temporal clustering coefficient is computed
 * @param ti A restrictive time interval
 * @return The temporal clustering coefficient for node with node id nid with respect to the time interval ti
 */
template<typename N, typename E>
double temporal_clustering_coefficient(IncidentLists<N, E> const& tg, NodeId nid, TimeInterval ti){

    std::set<NodeId> neighbors;
    for (auto &e : tg.getNode(nid).outEdges) {
        if (e.t < ti.first || e.t > ti.second) continue;
        neighbors.insert(e.v);
    }

    double count = 0;
    for (auto &v : neighbors) {
        for (auto &e : tg.getNode(v).outEdges) {
            if (neighbors.find(e.v) != neighbors.end()) {
                count += 1;
            }
        }
    }

    if (count == 0) return 0;

    auto timesteps = ti.second - ti.first;
    auto m = (double)(neighbors.size() * (neighbors.size() - 1));
    double result = (1.0 / (double)timesteps) * (count / m);

    return result;
}


/**
 * @brief Computes the temporal clustering coefficient for all nodes
 *
 * The temporal clustering coefficient is defined as
 * \f[
 * C_C(u) = \frac{\sum_{t\in T(\mathcal{G})} \pi_t(u)}{|T(\mathcal{G})|{|N(u)| \choose 2}},
 * \f]
 * where \f$\pi_t(u)=|\{(v,w,t,\lambda)\in\mathcal{E}\mid v,w\in N(u)\}|\f$
 * and \f$N(u)\f$ the neighbors of \f$u\f$ [1].
 *
 * [1] Tang, John, et al. "Temporal distance metrics for social network analysis."
 * Proceedings of the 2nd ACM workshop on Online social networks. 2009.
 *
 * @tparam N Node type
 * @param tg The temporal graph
 * @param ti A restrictive time interval
 * @return The temporal clustering coefficients for all nodes with respect to the time interval ti
 */
template<typename N, typename E>
std::vector<double> temporal_clustering_coefficient(IncidentLists<N, E> const& tg, TimeInterval ti){

    std::vector<double> result(tg.getNumberOfNodes(), 0);
    auto timesteps = ti.second - ti.first;

    for (size_t nid = 0; nid < tg.getNumberOfNodes(); ++nid) {
        std::set<NodeId> neighbors;

        for (auto &e : tg.getNode(nid).outEdges) {
            if (e.t < ti.first || e.t > ti.second) continue;
            neighbors.insert(e.v);
        }

        double count = 0;
        for (auto &v : neighbors) {
            for (auto &e : tg.getNode(v).outEdges) {
                if (e.t < ti.first || e.t > ti.second) continue;
                if (neighbors.find(e.v) != neighbors.end()) {
                    count += 1;
                }
            }
        }

        if (neighbors.empty() || neighbors.size() == 1) {
            result[nid] = 0.0;
        } else {
            auto m = (double)(neighbors.size() * (neighbors.size() - 1));
            result[nid] = (1.0 / (double)timesteps) * (count / m);
        }
    }

    return result;
}


}

#endif //TGLIB_TEMPORALCLUSTERINGCOEFFICIENT_H
