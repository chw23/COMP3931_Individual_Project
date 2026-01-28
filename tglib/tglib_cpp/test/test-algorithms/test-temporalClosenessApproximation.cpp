/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

#include <catch2/catch_test_macros.hpp>
#include <catch2/catch_approx.hpp>
#include <iostream>
#include "../TemporalGraphsInstances.h"
#include "../../src/algorithms/TemporalCloseness.h"
#include "../../src/algorithms/TemporalClosenessApproximation.h"
#include "../../src/core/Transformations.h"

using namespace tglib;
using namespace std;

TEST_CASE( "rnd tg compare with exact", "[temporal_closeness_approximation]" ) {
    int n = 10;
    int m = 100;
    int h = 50000;

    auto tgs = getRandomGraphExample(n, m);
    auto tg = to_incident_lists<TGNode>(tgs);

    vector<double> closeness;
    for (size_t i = 0; i < tg.getNumberOfNodes(); ++i) {
        auto c = temporal_closeness(tg, i, tg.getTimeInterval(), Distance_Type::Fastest);
        closeness.push_back(c);
    }

    auto approx = temporal_closeness_aproximation(tg, h, tg.getTimeInterval());
    for (int i = 0; i < n; ++i) {
        bool delta = (closeness[i]/n >= (approx[i]/n - 0.1)) || (closeness[i]/n <= (approx[i]/n + 0.1));
        REQUIRE(delta); // todo could fail with low probability
    }
}

