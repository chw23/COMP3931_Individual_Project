/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

/** @file TemporalClosenessApproximation.h
 *  @brief Contains function declarations for approximation of closeness centrality
 */

#ifndef TGLIB_TEMPORALCLOSENESSAPPROXIMATION_H
#define TGLIB_TEMPORALCLOSENESSAPPROXIMATION_H

#include "../core/OrderedEdgeList.h"
#include "../core/IncidentLists.h"
#include "../core/TRSGraph.h"
#include "../algorithms/TemporalDistances.h"

namespace tglib {

/**
 * Approximation of the temporal closeness wrt the minimum duration distance from [1].
 *
 * [1] Oettershagen, Lutz, and Petra Mutzel. "Efficient top-k temporal closeness calculation in temporal networks."
 * 2020 IEEE International Conference on Data Mining (ICDM). IEEE, 2020.
 *
 * @tparam N The temporal node type
 * @tparam E The temporal edge type
 * @param h The sample size
 * @param tg The input graph
 * @param ti The time interval
 * @return Approximation of the normalized temporal closeness wrt minimum duration distance
 */
template<typename N, typename E>
std::vector<double> temporal_closeness_aproximation(tglib::IncidentLists<N, E> &tg, unsigned int h,
                                     tglib::TimeInterval ti) {

    std::vector<double> result(tg.getNumberOfNodes(), 0);

    // calculate the temporal reverse graph
    auto rtg = reverse(tg, ti);

    // get h random vertices
    for (std::size_t i = 0; i < h; ++i) {
        // sample node
        NodeId n = rand() % rtg.getNumberOfNodes();

        // calculate the durations to all other nodes from each node in nids
        auto minduration = minimum_durations(rtg, n, rtg.getTimeInterval());

        for (size_t nid = 0; nid < tg.getNumberOfNodes(); ++nid) {
            if (minduration[nid] == inf || minduration[nid] == 0) continue;
            result[nid] += (1.0 / minduration[nid]);
        }
    }
    return result;
}


} // tglib


#endif //TGLIB_TEMPORALCLOSENESSAPPROXIMATION_H
