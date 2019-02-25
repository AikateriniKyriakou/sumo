#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2010-2019 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    randomRides.py
# @author  Jakob Erdmann
# @date    2019-02-24
# @version $Id$

from __future__ import print_function
from __future__ import absolute_import
import os, sys
import random
import optparse

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib  # noqa


def get_options(args=None):
    optParser = optparse.OptionParser()
    optParser.add_option("-a", "--additional-files", dest="additional",
                         help="define additional files for loading busStops")
    optParser.add_option("-o", "--output-file", dest="outfile",
                         help="define the output trip filename")
    optParser.add_option("--prefix", dest="tripprefix",
                         default="", help="prefix for the trip ids")
    optParser.add_option("-t", "--trip-attributes", dest="tripattrs",
                         default="", help="additional trip attributes. When generating pedestrians, attributes for " +
                         "<person> and <walk> are supported.")
    optParser.add_option("-b", "--begin", type="float", default=0, help="begin time")
    optParser.add_option("-e", "--end", type="float", default=3600, help="end time (default 3600)")
    optParser.add_option(
        "-p", "--period", type="float", default=1, help="Generate vehicles with equidistant departure times and " +
        "period=FLOAT (default 1.0). If option --binomial is used, the expected arrival rate is set to 1/period.")
    optParser.add_option("-s", "--seed", type="int", help="random seed")
    optParser.add_option("--min-distance", type="float", dest="min_distance",
                         default=0.0, help="require start and end edges for each trip to be at least <FLOAT> m apart")
    optParser.add_option("--max-distance", type="float", dest="max_distance",
                         default=None, help="require start and end edges for each trip to be at most <FLOAT> m " +
                         "apart (default 0 which disables any checks)")
    optParser.add_option("-v", "--verbose", action="store_true",
                         default=False, help="tell me what you are doing")
    (options, args) = optParser.parse_args(args=args)

    if not options.additional or not options.outfile:
        optParser.print_help()
        sys.exit(1)

    if options.period <= 0:
        print("Error: Period must be positive", file=sys.stderr)
        sys.exit(1)

    return options

def main(options):
    if options.seed:
        random.seed(options.seed)
    busStops = [bs.id for bs in sumolib.xml.parse_fast(options.additional, 'busStop', ['id'])]
    if len(busStops) < 2:
        print("Error: At least two busStops are required", file=sys.stderr)
        sys.exit(1)

    depart = options.begin
    idx = 0
    with open(options.outfile, 'w') as outf:
        outf.write('<routes>\n')
        while depart < options.end:
            bsFrom = random.choice(busStops)
            bsTo = random.choice(busStops)
            while bsTo == bsFrom:
                bsTo = random.choice(busStops)
            outf.write('    <person id="%s%s" depart="%s">\n' % (
                options.tripprefix, idx, depart))
            outf.write('        <stop busStop="%s" duration="5"/>\n' % bsFrom)
            outf.write('        <ride busStop="%s" lines="ANY"/>\n' % (bsTo))
            outf.write('    </person>\n')
            depart += options.period
            idx += 1
        outf.write('</routes>\n')

if __name__ == "__main__":
    if not main(get_options()):
        sys.exit(1)