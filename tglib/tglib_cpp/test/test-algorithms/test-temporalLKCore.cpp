/* Copyright (C) 2022 Lutz Oettershagen - All Rights Reserved
 *
 * This file is part of TGLib which is released under MIT license.
 * See file LICENSE.md or go to https://gitlab.com/tgpublic/tglib
 * for full license details.
 */

#include <catch2/catch_test_macros.hpp>
#include <iostream>
#include "../TemporalGraphsInstances.h"
#include "../../src/core/Transformations.h"
#include "../../src/algorithms/TemporalLKCore.h"

using namespace tglib;
using namespace std;

TEST_CASE( "temporal LK lasting core", "[temporal_LKlastingcore]" ) {
    auto tgs = getLKCoreTg();

    auto c = compute_LKcores<TemporalEdge>(tgs, 2, 2);

    REQUIRE(c[0] == 0);
    REQUIRE(c[1] == 1);
    REQUIRE(c[2] == 2);
}

